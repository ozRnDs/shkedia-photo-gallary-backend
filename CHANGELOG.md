## 0.6.0 (2024-01-07)

### Feat

- **Upload**: Create upload function and UI. Integrate with upload service, Added devices information to the request
- **search_bar**: Add basic selections to navigate throught the collection
- **media_view**: Add jobs details to the media view
- **view_media**: Add grouped view insights and engines. Including collapsable tables
- **bussiness/db**: Add InsightEngineService that holds the entire engines information
- **view_media**: Add dynamic bounding box display
- **view_media**: Get insights and jobs for media and display on media page

### Fix

- **MediaDBService**: Use the session with retry for the get operations
- **InsightEngineService**: Add missing imports
- **AuthService**: Fixtypo in the redirect to the login screen
- **views/albums**: Catch ConnectionError
- **AuthService**: Improve exceptions handling of invalid sessions and save current path to be used in the login page
- **Token**: Add hash function to be used by TTLCache
- **MediaDBService**: Convert request ConnectionError to global ConnectionError to be handled later
- **InsightEngineService**: Fix get_engine_name_by_id. Return name instead of id

### Refactor

- **gallery/service**: Delete custom caching function
- **base/views,base/templates**: Create BaseContext class to sturcture the data in the views
- **view_media**: Improve the insights presentation
- **MediaViewService,-InsightEngineService**: Add cache mechanism
- **business/gallery**: Extract the functions that are used by the view_media to decoupled service
- **views**: Delete unused class
- **business/gallery**: Extract Page and MediaView classes from the service
- **gallery/service**: Clean unused classes

### Perf

- **MediaGalleryService,-MediaViewService**: Add caching. Catch decrypt failure
- **MediaDBService**: Add cache to get_all_engines

## 0.5.2 (2024-01-05)

### Refactor

- **dev/mock_user**: Adjust to project_shkedia_models
- **src**: Adjust project to use project_shkedia_models library. Adapt project to new db_media api
- **gallery/service**: Add traceback print to the _refresh_cache_ function

## 0.5.1 (2023-12-13)

### Fix

- **GalleryService,view_media.html**: Get device information using the "get_device" method. Redesign the media details on the page
- **templates/side_offcanvas**: Bring back missing Close button to the canvas
- **GalleryService**: Call refresh_cache for every albums read. Fix the unlock and lock order to enable correct refresh of the cache mechanism

## 0.5.0 (2023-12-10)

### Feat

- **views,gallery_service,view_media,side_offcanvas**: Add offcanvas navigation to the view_media page
- **view_album**: Add sidebar (offcanvas) for navigating between albums
- **business/GalleryService**: Reactivate the caching mechanism in order to lower communication with Postgres
- **templates/navbar**: Create dropdown menu for the about section. Adjust the navbar to the new bootstrap version
- **statis/bootstrap**: Update the bootstrap version

### Refactor

- **main.html**: Include bootstrap.js in the main.html
- **about_creator**: Rewrite the content

## 0.4.2 (2023-12-10)

### Fix

- **GalleryService**: Sort the items lists according to date
- **AuthService**: Catch and handle ValueError while checking the token

### Refactor

- **ViewMedia**: Diable tags in the media page
- **Login**: Add demo flash message

## 0.4.1 (2023-12-10)

### Fix

- **Login**: Add messages for token expired and for wrong user/password
- **encryptionService,-galleryService**: Add support to legacy encrypted images and handle errors in the caching mechanism

### Refactor

- **abouts**: Creating about the creator, Rephrase the about and trying to be moree clear
- **templates/footer**: Adding technologies to the project, Rephrase the short about
- **main/urls**: Disable the django default admin section
- **settings.py**: Pull the debug value from project configuration. Add dev host
- **templates/navbar**: Show the Photos in the navbar only for logged in users

## 0.4.0 (2023-12-08)

### Feat

- **MediaRequest**: Add exif field

### Fix

- **encryption/service**: Switch the order between the comprasion and the encryption

### Refactor

- **templates/search**: Hide search bar
- **templates/view_media**: Show media name instead of description

## 0.3.0 (2023-12-05)

### Feat

- **GalleryService,-base/views**: Create different cache for every user

## 0.2.1 (2023-12-05)

### Fix

- **GalleryService**: Manage cache for multiple users

## 0.2.0 (2023-12-05)

### Feat

- **templates/footer.html**: Added GitHub Link

### Fix

- **GalleryService**: Handle case that local file does not exists

## 0.1.3 (2023-12-04)

### Fix

- **templates/search**: Putting CSRF token in the login form

## 0.1.2 (2023-12-04)

### Fix

- **settings**: Add CSRF_TRUSTED_ORIGINS to the django settings file

## 0.1.1 (2023-12-04)

### Fix

- **view_media-and-static/css**: Created special class for the images on displayed
- **templates/search**: Deleted csrf token

## 0.1.0 (2023-12-03)

### Feat

- **templates/albums,templates/view_album**: Activate the next and previous buttons
- **templates/view_media**: Display the user and device information. Add back button
- **gallery_service**: Add the full user and device data in get_media_content function
- **templates/about_media**: Create a section about the media's lifecycle
- **templates/about**: Add the page context
- **About**: Add about page and link it to the webservice
- **base/views**: Integrate the auth_service in the private pages
- **business/authentication**: Create custom authentication service that uses the auth API
- **business/db/user_service**: Add retry mechanism to login. Fix search_user signature to complient with auth API
- **src**: Create web app with 3 pages. Albums, Albums Views, Photo View

### Fix

- **GalleryService**: Set the caching retention for production mode
- **base/views**: Send user's real token to the RestAPI operations. Send the user and device data to the view_media page
- **bootstrap.min.css**: Change the img-fluid width to min-width: 100
- **views/about,AuthService**: Add is_authenticated decorator, inorder to display the correct "login"/"logout" button in the navbar

### Refactor

- **templates/footer,navbar**: Personalize the statis imformation in the footer and navbar
- **search**: Enable search only on desired views per demand
- **business/authentication/service**: Set login_redirect_path in the service contructor and not in the decorator
- **django**: Create the django base template
- **Project-Template**: Create the project from template
