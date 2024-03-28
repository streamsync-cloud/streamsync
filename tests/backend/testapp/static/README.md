# Serving static files

You can use this folder to store files which will be served statically in the "/static" route.

This is useful to store images and other files which will be served directly to the user of your application.

For example, if you store an image named "myimage.jpg" in this folder, it'll be accessible as "static/myimage.jpg".
You can use this relative route as the source in an Image component.

# Favicon

The favicon is served from this folder. Feel free to change it. Keep in mind that web browsers cache favicons differently
than other resources. Hence, the favicon change might not reflect immediately.