import mimetypes
import os

import fastapi
import fastapi.testclient
import pytest
import streamsync.serve
from fastapi import FastAPI
from streamsync.serve import ExtensionManager

from tests.backend import test_app_dir, test_multiapp_dir
from tests.fixtures.base import fixture


class TestServe:

    def test_valid(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            assert res.status_code == 200
            session_id = res.json().get("sessionId")
            assert session_id is not None
            with client.websocket_connect("/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": session_id
                    }
                })
                websocket.send_json({
                    "type": "event",
                    "trackingId": 1,
                    "payload": {
                        "type": "ss-number-change",
                        "instancePath": [
                            {"componentId": "root", "instanceNumber": 0}
                        ],
                        "payload": 9
                    }
                })
                a = websocket.receive_json()
                assert a.get("messageType") == "eventResponse"
                websocket.close(1000)

    def test_bad_session(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            with client.websocket_connect("/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()

    def test_session_verifier_header(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json",
                "X-Fail": "yes"
            })
            assert res.status_code == 403

    def test_session_verifier_cookies(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app, cookies={
            "fail_cookie": "yes"
        }) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json"
            })
            assert res.status_code == 403

    def test_session_verifier_pass(self) -> None:
        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(
            test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app, cookies={
            "another_cookie": "yes"
        }) as client:
            res = client.post("/api/init", json={
                "proposedSessionId": None
            }, headers={
                "Content-Type": "application/json",
                "X-Success": "yes"
            })
            assert res.status_code == 200

    def test_serve_javascript_file_with_a_valid_content_type(self) -> None:
        # Arrange
        mimetypes.add_type("text/plain", ".js")

        asgi_app: fastapi.FastAPI = streamsync.serve.get_asgi_app(test_app_dir, "run")
        with fastapi.testclient.TestClient(asgi_app) as client:
            # Acts
            res = client.get("/static/file.js")

            # Assert
            assert res.status_code == 200
            assert res.headers["Content-Type"].startswith("text/javascript")

    def test_multiapp_should_run_the_lifespan_of_all_streamsync_app(self):
        """
        This test check that multiple streamsync applications embedded
        in FastAPI start completely and answer websocket request.
        """
        asgi_app: fastapi.FastAPI = FastAPI(lifespan=streamsync.serve.lifespan)
        asgi_app.mount("/app1", streamsync.serve.get_asgi_app(test_multiapp_dir / 'app1', "run"))
        asgi_app.mount("/app2", streamsync.serve.get_asgi_app(test_multiapp_dir / 'app2', "run"))

        with fastapi.testclient.TestClient(asgi_app) as client:
            # test websocket connection on app1
            with client.websocket_connect("/app1/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()

            # test websocket connection on app2
            with client.websocket_connect("/app2/api/stream") as websocket:
                websocket.send_json({
                    "type": "streamInit",
                    "trackingId": 0,
                    "payload": {
                        "sessionId": "bad_session"
                    }
                })
                with pytest.raises(fastapi.WebSocketDisconnect):
                    websocket.receive_json()


class TestExtensionManager:

    def test_load_extensions_load_the_extensions_from_user_extension_directory(self):
        """
        Extension manager should loads extensions from the directory extension in user application if it exists
        """
        # Arrange
        app_dir = fixture('app_dir_with_extensions')
        extension_manager = ExtensionManager()

        # Act
        extension_manager.load_extensions(app_dir, [])

        # Assert
        extensions = extension_manager.extensions_list()
        assert len(extensions) == 1
        assert extensions == [None]

    def test_load_extensions_load_the_extensions_from_streamsync_extension_packages(self):
        """
        Extension manager should loads extensions from installed packaged that start with 'streamsync_' and contains a directory extension
        """
        # Arrange
        app_dir = fixture('app_dir_with_extensions')
        site_packages_dir = fixture('site_packages')
        modules_dir = [os.path.join(site_packages_dir, directory) for directory in os.listdir(site_packages_dir)]
        extension_manager = ExtensionManager()

        # Act
        extension_manager.load_extensions(app_dir, modules_dir)

        # Assert
        extensions = extension_manager.extensions_list()
        assert len(extensions) == 2
        assert extensions == [None, 'streamsync_demo']

    def test_extensions_assets_urls_return_assets_urls_from_all_extensions(self):
        """
        Extension manager should return the urls of the assets from all extensions
        """
        # Arrange
        app_dir = fixture('app_dir_with_extensions')
        site_packages_dir = fixture('site_packages')
        modules_dir = [os.path.join(site_packages_dir, directory) for directory in os.listdir(site_packages_dir)]
        extension_manager = ExtensionManager()
        extension_manager.load_extensions(app_dir, modules_dir)

        # Act
        assets_urls = extension_manager.extensions_assets_urls()

        # Assert
        assert len(assets_urls) == 4

        assets_urls = sorted(assets_urls)
        assert assets_urls == [
            'component1.umd.js',
            'streamsync_demo/component1.umd.js',
            'streamsync_demo/style.css',
            'style.css',
        ]

    def test_extension_assets_urls_return_urls_of_extension_assets_as_simple_file_for_the_user_extension_directory(self):
        """
        Extension manager should return the urls of the assets as simple file for the user extension directory
        """
        # Arrange
        app_dir = fixture('app_dir_with_extensions')
        extension_manager = ExtensionManager()
        extension_manager.load_extensions(app_dir, [])

        # Act
        assets_urls = extension_manager.extension_assets_urls(None)

        # Assert
        assert len(assets_urls) == 2

        assets_urls = sorted(assets_urls)
        assert assets_urls == [
            'component1.umd.js',
            'style.css',
        ]

    def test_extension_assets_urls_return_urls_of_extension_assets_as_qualified_path_for_streamsync_extension_packages(self):
        """
        Extension manager should return the urls of the assets of a streamsync extension packages as qualified path
        """
        # Arrange
        app_dir = fixture('app_dir_simple')
        site_packages_dir = fixture('site_packages')
        modules_dir = [os.path.join(site_packages_dir, directory) for directory in os.listdir(site_packages_dir)]
        extension_manager = ExtensionManager()
        extension_manager.load_extensions(app_dir, modules_dir)

        # Act
        assets_urls = extension_manager.extension_assets_urls('streamsync_demo')

        # Assert
        assert len(assets_urls) == 2

        assets_urls = sorted(assets_urls)
        assert assets_urls == [
            'streamsync_demo/component1.umd.js',
            'streamsync_demo/style.css',
        ]

    def test_extension_asset_from_url_should_return_the_path_of_the_asset_to_serve_it_as_file(self):
        """
        Extension manager should return the path of the asset. Fastapi will serve this file to the browser.
        """
        # Arrange
        app_dir = fixture('app_dir_simple')
        site_packages_dir = fixture('site_packages')
        modules_dir = [os.path.join(site_packages_dir, directory) for directory in os.listdir(site_packages_dir)]
        extension_manager = ExtensionManager()
        extension_manager.load_extensions(app_dir, modules_dir)

        # Act
        asset_path = extension_manager.extension_asset_from_url('streamsync_demo/component1.umd.js')

        # Assert
        assert asset_path == os.path.join(site_packages_dir, 'streamsync_demo', 'extensions', 'component1.umd.js')

    def test_extension_asset_from_url_return_none_when_asset_is_missing(self):
        """
        Extension manager should return None when required asset is missing. FastApi will raise 404 error on this.
        """
        # Arrange
        app_dir = fixture('app_dir_simple')
        site_packages_dir = fixture('site_packages')
        modules_dir = [os.path.join(site_packages_dir, directory) for directory in os.listdir(site_packages_dir)]
        extension_manager = ExtensionManager()
        extension_manager.load_extensions(app_dir, modules_dir)

        # Act
        asset_path = extension_manager.extension_asset_from_url('streamsync_demo/component3.umd.js')

        # Assert
        assert asset_path is None
