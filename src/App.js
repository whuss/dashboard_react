import React, { useState } from "react";
import ReactDOM from "react-dom";

import Jumbotron from "react-bootstrap/Jumbotron";
import Toast from "react-bootstrap/Toast";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";

import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import Navigation from "./Navigation";
import Dashboard from "./Dashboard";
import SwitchCycles from "./SwitchCycles";
import AnalyticsScenes from "./AnalyticsScenes";
import AnalyticsConnection from "./AnalyticsConnection";
import AnalyticsKeyboard from "./AnalyticsKeyboard";
import SystemStability from "./SystemStability";
import Plot from "./BokehPlot";

import useDataApi, { FetchHackernews } from "./Fetch";

import "./App.css";

function Title(props) {
    const titleBar = document.getElementById("titlebar-root");
    return ReactDOM.createPortal(<h2>{props.title}</h2>, titleBar);
}

function NavPortal() {
    const titleBar = document.getElementById("navbar-root");
    return ReactDOM.createPortal(<Navigation />, titleBar);
}

function AppRouter() {
    return (
        <Router>
            <NavPortal />
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Container fluid className="p-3">
                <Switch>
                    <Route path="/about">
                        <Title title="About" />
                        <About />
                        <FetchHackernews />
                    </Route>
                    <Route path="/analytics/scenes">
                        <Title title="Analytics Scenes" />
                        <AnalyticsScenes />
                    </Route>
                    <Route path="/analytics/connection">
                        <Title title="Analytics Connection" />
                        <AnalyticsConnection />
                    </Route>
                    <Route path="/analytics/Keyboard">
                        <Title title="Analytics Keyboard" />
                        <AnalyticsKeyboard />
                    </Route>
                    <Route path="/statistics/switch_cycles">
                        <Title title="Statistics On/Off Cycles" />
                        <SwitchCycles />
                    </Route>
                    <Route path="/system/stability">
                        <Title title="System Stability" />
                        <SystemStability />
                    </Route>
                    <Route path="/database_size">
                        <Title title="Database Size" />
                        <Plot src="/backend/plot_database_size" />
                    </Route>
                    <Route path="/">
                        <Title title="Dashboard" />
                        <Dashboard />
                    </Route>
                </Switch>
            </Container>
        </Router>
    );
}

function Example() {
    return (
        <Alert dismissible variant="danger">
            <Alert.Heading>Error!</Alert.Heading>
            <p>
                Change and <i>try</i> again.
            </p>
        </Alert>
    );
}

const ExampleToast = ({ children }) => {
    const [show, toggleShow] = useState(true);

    return (
        <>
            {!show && <Button onClick={() => toggleShow(true)}>Show Toast</Button>}
            <Toast show={show} onClose={() => toggleShow(false)}>
                <Toast.Header>
                    <strong className="mr-auto">React-Bootstrap</strong>
                </Toast.Header>
                <Toast.Body>{children}</Toast.Body>
            </Toast>
            <Example />
        </>
    );
};

function About() {
    return (
        <Jumbotron>
            <h1 className="header">Welcome To React-Bootstrap</h1>
            <ExampleToast>
                We now have Bootstrap
                <span role="img" aria-label="tada">
                    🎉
                </span>
            </ExampleToast>
        </Jumbotron>
    );
}

const App = () => <AppRouter />;

export default App;
