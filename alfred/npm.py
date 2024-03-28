import alfred
import os

@alfred.command("npm.lint", help="lint check npm packages")
def npm_lint():
    alfred.run("npm run ui:lint:ci")

@alfred.command("npm.test", help="test check npm packages")
def npm_test():
    alfred.run("npm test")

@alfred.command("npm.e2e", help="run e2e tests")
@alfred.option('--browser', '-b', help="run e2e tests on specified browser", default='chromium')
def npm_e2e(browser):
    with alfred.env(CI="true"):
        alfred.run("npm run e2e:"+browser)

@alfred.command("npm.build", help="build ui code")
def npm_build():
    alfred.run("npm run ui:build")

@alfred.command("npm.build_custom_components", help="build custom components")
def ui_build_custom():
    alfred.run("npm run ui:custom.build")

@alfred.command("npm.codegen.binding.ui", help="generate binding for low code ui")
def ui_build_custom():
    alfred.run("npm run codegen.binding.ui")
