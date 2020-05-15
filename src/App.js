import "./App.css";

import React, { useState } from "react";
import ReactDOM from "react-dom";

import Jumbotron from "react-bootstrap/Jumbotron";
import Toast from "react-bootstrap/Toast";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";

import useDateRange, { formatDate } from "./DatePicker";

import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import Navigation from "./Navigation";
import Dashboard from "./Dashboard";
import SwitchCycles from "./SwitchCycles";
import AnalyticsSensor from "./AnalyticsSensor";
import AnalyticsScenes from "./AnalyticsScenes";
import AnalyticsConnection from "./AnalyticsConnection";
import AnalyticsKeyboard from "./AnalyticsKeyboard";
import AnalyticsKeypress from "./AnalyticsKeypress";
import AnalyticsMouse from "./AnalyticsMouse";
import AnalyticsPowerTimeline from "./AnalyticsPowerTimeline";
import SystemStability from "./SystemStability";
import SystemRestarts from "./SystemRestarts";
import SystemErrors from "./SystemErrors";
import SystemLogs from "./SystemLogs";
import ClusteringInputDistributions from "./ClusteringInputDistributions";
import ClusteringScatterPlot from "./ClusteringScatterPlot";
import ClusteringFrequency from "./ClusteringFrequency";
import ClusteringTimeline from "./ClusteringTimeline";
import Plot from "./BokehPlot";

import { useDevice, LoadingAnimation } from "./Toolbar";

function Title(props) {
    const titleBar = document.getElementById("titlebar-root");
    return ReactDOM.createPortal(<h2>{props.title}</h2>, titleBar);
}

function NavPortal() {
    const titleBar = document.getElementById("navbar-root");
    return ReactDOM.createPortal(<Navigation />, titleBar);
}

function NavRoute(props) {
    return (
        <Route path={props.path}>
            <Title title={props.title} />
            {props.children}
        </Route>
    );
}

const MainView = (props) => {
    const devices = props.devices;
    return (
        <Container fluid className="p-3">
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Switch>
                <NavRoute path="/about" title="About">
                    <About />
                </NavRoute>
                <NavRoute
                    path={["/analytics/sensor/:device/:sensor/:sample_rate/:start_date/:end_date", "/analytics/sensor"]}
                    title="Analytics Sensor"
                >
                    <AnalyticsSensor devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/scenes" title="Analytics Scenes">
                    <AnalyticsScenes devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/power" title="Analytics Power timeline">
                    <AnalyticsPowerTimeline devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/connection" title="Analytics Connection">
                    <AnalyticsConnection devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/keyboard" title="Analytics Keyboard">
                    <AnalyticsKeyboard devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/keypress" title="Analytics Keypress">
                    <AnalyticsKeypress devices={devices}/>
                </NavRoute>
                <NavRoute path="/analytics/mouse" title="Analytics Mouse">
                    <AnalyticsMouse devices={devices}/>
                </NavRoute>
                <NavRoute path="/clustering/input_distributions" title="Clustering Input Distributions">
                    <ClusteringInputDistributions devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/scatter_plot" title="Clustering Scatter Plot">
                    <ClusteringScatterPlot devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/frequency" title="Daily Cluster Frequency">
                    <ClusteringFrequency devices={devices} />
                </NavRoute>
                <NavRoute path="/clustering/timeline" title="Daily Cluster Timeline">
                    <ClusteringTimeline devices={devices} />
                </NavRoute>
                <NavRoute path="/statistics/switch_cycles" title="Statistics On/Off Cycles">
                    <SwitchCycles devices={devices}/>
                </NavRoute>
                <NavRoute path="/system/stability" title="System Stability">
                    <SystemStability devices={devices}/>
                </NavRoute>
                <NavRoute path="/system/restarts" title="System Restarts">
                    <SystemRestarts devices={devices}/>
                </NavRoute>
                <NavRoute path="/system/errors" title="System Errors">
                    <SystemErrors devices={devices}/>
                </NavRoute>
                <NavRoute path="/database_size" title="Database Size">
                    <Plot src="/backend/plot_database_size" />
                </NavRoute>
                <NavRoute
                    path={[
                        "/logs/:device/:duration/:log_level/:timestamp",
                        "/logs/:device/:duration/:log_level",
                        "/logs/:device/:duration",
                        "/logs/:device",
                        "/logs",
                    ]}
                    title="Logs"
                >
                    <SystemLogs devices={devices}/>
                </NavRoute>
                <NavRoute path="/" title="Dashboard">
                    <Dashboard devices={devices}/>
                </NavRoute>
            </Switch>
        </Container>
    );
}

function AppRouter() {
    const [devices, isLoading, isError] = useDevice();
    return (
        <Router>
            <NavPortal />
            <LoadingAnimation isLoading={isLoading} isError={isError}><MainView devices={devices}/></LoadingAnimation>
        </Router>
    );
}

function Example() {
    return (
        <div>Altert</div>
        // s
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
    const [from, to, dateRange] = useDateRange(new Date("2020-04-05T00:00:00"), new Date("2020-05-04T00:00:00"));

    return (
        <div>
            {dateRange}
            <Jumbotron>
                <h1 className="header">Welcome To React-Bootstrap</h1>
                <ExampleToast>
                    We now have Bootstrap
                    <span role="img" aria-label="tada">
                        🎉
                    </span>
                </ExampleToast>
            </Jumbotron>
        </div>
    );
}

const App = () => <AppRouter />;

export default App;
