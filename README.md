# inCollege

A simple Python application that manages use logins, account creations, and other functionalities for the "inCollege Application" Written by New Mexico Software Engineering, Inc.

## Features

- User Login
- Account Creation
- Password Validation
- SQLite Database Support

## Requirements

- Python 3.x
- venv

## Installation

### Windows:

1. Resolve dependencies:

    ```batch
    resolve_dependencies.bat
    ```

2. Run the application:

    ```batch
    run.bat
    ```

### Linux/Mac:

1. Resolve dependencies:

    ```bash
    chmod +x resolve_dependencies.sh
    ./resolve_dependencies.sh
    ```

2. Run the application:

    ```bash
    chmod +x run.sh
    ./run.sh
    ```

## Project Structure

- `main.py`: The entry point of the application.
- `users.db`: SQLite database storing user accounts.
- `resolve_dependencies.bat` & `resolve_dependencies.sh`: Batch and shell script to install dependencies.
- `run.bat` & `run.sh`: Batch and shell script to run the application.
- `requirements.txt`: Required Python packages.

## Documentation

Refer to inline comments within the code for further documentation on how the classes and methods work.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)
