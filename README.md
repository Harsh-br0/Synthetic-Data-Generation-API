
### Setup

- Create a dependency layer for lambda function by zipping the `python` folder created by this cmd and upload it to lambda layers.
    ```
    pip install -r .\requirements.txt -t python --platform=manylinux2014_x86_64 --only-binary=:all:
    ```

- Zip the `src` folder and `main.py` and upload the zip as code source to lambda and attach the layer created above.
- Make sure the Env variables are properly configured there and function URL should be public and function handler should be `main.handler`.
- Increase the function timeout to 3 mins.

### Usage
- Open the function URL with `/docs` appended to it.

### Env Variables

- `OPENAI_API_KEY`

    OpenAI API Key that is used for chat completion API.

- `ENCRYPTED_COOKIE_KEY`

    A url safe base 64 encoded 32 bytes key used for encrypting cookies, can be generated with `Fernet.generate_key()`.
