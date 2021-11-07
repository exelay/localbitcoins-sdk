# localbitcoins-sdk
A simple library for working with LocalBitcoins API

I created this library to make it easier to use the **LocalBitcoins API**.
The library is very simple. 
It has just one object `Client`, with one custom method `send_request`.

## How to use it?
### Install it
```shell
pip install localbitcoins-sdk
```
### Use it
```python
# Import the Client
from lb_sdk import Client

# Create a Client object with the hmac key and the hmac secret from localbitcoins.
client = Client('your-hmac-key-here', 'your-hmac-secret-here')

# Send a request and get a response data.
data = client.send_request('/api/myself/')

# By default the client uses the get request method, but you can send a post request.
data = client.send_request('/api/logout/', 'post')

# Or you can send a request with any parameters.
params = {
    'trade_type': 'LOCAL_SELL',
    'currency':	'RUB',
    'countrycode': 'RU',
}
data = client.send_request('/api/ads/', params=params)
```