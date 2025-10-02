# TODO: Fix Errors in Facial Recognition Project

## 1. Fix CORS Error for FontAwesome Script ✅
- **File:** frontend/index.html
- **Issue:** External FontAwesome script blocked by CORS policy.
- **Fix:** Removed `crossorigin="anonymous"` attribute from the script tag to allow loading from local origin.

## 2. Fix 404 Error for favicon.ico ✅
- **File:** frontend/favicon.ico
- **Issue:** favicon.ico file missing in frontend folder.
- **Fix:** Created a placeholder favicon.ico file in frontend folder.

## 3. Fix 401 Unauthorized Error for Admin API ✅
- **Files:** frontend/index.html, frontend/scripts/app.js
- **Issue:** Admin panel fetches /api/admin/known_faces without authentication.
- **Fix:** 
  - Added login form to admin section in HTML.
  - Modified JS to check login status on admin tab switch, show login form if not logged in, handle login POST to /api/admin/login with credentials, then fetch users with credentials included in all admin API calls.

## 4. Test Fixes
- Run the Flask app and verify errors are resolved.
- Check browser console for any remaining issues.
- Default admin credentials: username 'admin', password 'password'.
