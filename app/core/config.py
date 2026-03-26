"""
This file for handle config like different secret key, url
and secret information
"""
from fastapi.security import OAuth2PasswordBearer
# secret key for create strong hash password
PASSWORD_SECRET_KEY = 'cafb54f2e09a3d50c39344853563deabc8e78434aad5c5bca3911c65796a9735'
DUMMY_HASH = '$2y$10$fcr1D9TCCYl2PMWr1s.22e1ewt8k3103i3apuGYOOv.votR8.ObuG'
# secret key for jwt token
SECRET_KEY = '45c0e3ac424bd777f59359cfb0665d9cd44429151cea6e023ea043989f7c5ab4'
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

