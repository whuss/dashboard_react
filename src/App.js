import React from "react";
import Container from "react-bootstrap/Container";
import Jumbotron from "react-bootstrap/Jumbotron";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import AnalyticsConnection from "./AnalyticsConnection";
import AnalyticsKeyboard from "./AnalyticsKeyboard";
import AnalyticsKeypress from "./AnalyticsKeypress";
import AnalyticsMouse from "./AnalyticsMouse";
import AnalyticsPowerTimeline from "./AnalyticsPowerTimeline";
import AnalyticsScenes from "./AnalyticsScenes";
import AnalyticsSensor from "./AnalyticsSensor";
import "./App.css";
import Plot from "./BokehPlot";
import ClusteringFrequency from "./ClusteringFrequency";
import ClusteringInputDistributions from "./ClusteringInputDistributions";
import ClusteringScatterPlot from "./ClusteringScatterPlot";
import ClusteringTimeline from "./ClusteringTimeline";
import Dashboard from "./Dashboard";
import DeviceDetails from "./DeviceDetails";
import Navigation from "./Navigation";
import SwitchCycles from "./SwitchCycles";
import SystemErrors from "./SystemErrors";
import SystemLogs from "./SystemLogs";
import SystemRestarts from "./SystemRestarts";
import SystemStability from "./SystemStability";
import { LoadingAnimation, useDevice } from "./Toolbar";

const Title = (props) => {
    const titleBar = document.getElementById("titlebar-root");
    return ReactDOM.createPortal(<h2>{props.title}</h2>, titleBar);
};

const NavPortal = (props) => {
    const titleBar = document.getElementById("navbar-root");
    return ReactDOM.createPortal(<Navigation />, titleBar);
};

const NavRoute = (props) => (
    <Route path={props.path}>
        <Title title={props.title} />
        {props.children}
    </Route>
);

const MainView = (props) => {
    const devices = props.devices;
    return (
        <Container fluid>
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
                    <AnalyticsSensor devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/scenes" title="Analytics Scenes">
                    <AnalyticsScenes devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/power" title="Analytics Power timeline">
                    <AnalyticsPowerTimeline devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/connection" title="Analytics Connection">
                    <AnalyticsConnection devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/keyboard" title="Analytics Keyboard">
                    <AnalyticsKeyboard devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/keypress" title="Analytics Keypress">
                    <AnalyticsKeypress devices={devices} />
                </NavRoute>
                <NavRoute path="/analytics/mouse" title="Analytics Mouse">
                    <AnalyticsMouse devices={devices} />
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
                    <SwitchCycles devices={devices} />
                </NavRoute>
                <NavRoute path="/system/stability" title="System Stability">
                    <SystemStability devices={devices} />
                </NavRoute>
                <NavRoute path="/system/restarts" title="System Restarts">
                    <SystemRestarts devices={devices} />
                </NavRoute>
                <NavRoute path="/system/errors" title="System Errors">
                    <SystemErrors devices={devices} />
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
                    <SystemLogs devices={devices} />
                </NavRoute>
                <NavRoute path={["/device_details/:device", "/device_details"]} title="Device Details">
                    <DeviceDetails devices={devices} />
                </NavRoute>
                <NavRoute path="/" title="Dashboard">
                    <Dashboard devices={devices} />
                </NavRoute>
            </Switch>
        </Container>
    );
};

const AppRouter = (props) => {
    const [devices, isLoading, isError] = useDevice();
    return (
        <Router>
            <NavPortal />
            <LoadingAnimation isLoading={isLoading} isError={isError}>
                <MainView devices={devices} />
            </LoadingAnimation>
        </Router>
    );
};

const About = (props) => (
    <Jumbotron>
        <h1 className="header">Todo ...</h1>
    </Jumbotron>
);

const App = () => <AppRouter />;

export default App;
export { MainView };
