
# Introduction

Source code of Reprolight Web app for PTL telemetry and data analytics.
The backend uses Flask to provide a JSON API, while the frontend is written using React.

## Deployment

The app is fully dockerized and can be deployed using docker-compose with the following commands:

```
$ docker-compose build
$ docker-compose up -d
```

When running, the webapp listens on port 8003.

The only prerequisites, except a working docker, is the existence of a directory `/docker-volume` that
needs to be writable by the docker-service.

To update the deployed:

```
$ git pull
$ docker-compose down
$ docker-compose build
$ docker-compute up -d
```

## Development

A development server, can be started in parallel to the deployed server on the same machine.
For this to work a local mysql server needs to be running.

### Setup development environment

Install nodejs and install the necessary npm packages:

```
$ npm ci
```

Setup a new python virtual environment and install all python library dependencies:

```
$ cd backend
$ pip install -r requirements.txt
```

### Installation of development server

Note: this steps are only needed the first time the development server is started on a new machine

Open `mysql` with root privileges and run the commands in `mysql_cache\sql\create_user.sql` to create
a mysql user account with the correct credentials.

To create the db tables run:

```
$ cd backend
$ export PYTHONPATH=.
$ python scripts/cache_queries.py init
```

## Start development server

Open a terminal and switch to the correct python virtual enviroment. Start the backend flask server with:

```
$ python app.py
```

The development server listens on port 5000. It can be tested by navigating to the url `http://127.0.0.1:5000/backend/devices`. This should return a json array consisting of the names of all registered PTL's.

To start the frontend server, open a second terminal and run:

```
npm start
```

The frontend server listens on port 3000.

Open url `http://127.0.0.1:3000` to see the dashboard.

Both backend and frontend development servers automatically reload when the source code is changed.


# Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

### `npm run eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.

## Learn More

You can learn more in the [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started).

To learn React, check out the [React documentation](https://reactjs.org/).

### Code Splitting

This section has moved here: https://facebook.github.io/create-react-app/docs/code-splitting

### Analyzing the Bundle Size

This section has moved here: https://facebook.github.io/create-react-app/docs/analyzing-the-bundle-size

### Making a Progressive Web App

This section has moved here: https://facebook.github.io/create-react-app/docs/making-a-progressive-web-app

### Advanced Configuration

This section has moved here: https://facebook.github.io/create-react-app/docs/advanced-configuration

### Deployment

This section has moved here: https://facebook.github.io/create-react-app/docs/deployment

$ serve -s build

### `npm run build` fails to minify

This section has moved here: https://facebook.github.io/create-react-app/docs/troubleshooting#npm-run-build-fails-to-minify
