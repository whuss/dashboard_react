import React, { Component, useState, useEffect, useRef } from "react";

import Jumbotron from "react-bootstrap/Jumbotron";
import Toast from "react-bootstrap/Toast";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";
import Table from "react-bootstrap/Table";

import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
//import ScriptTag from "react-script-tag";

import Navigation from "./Navigation";
import { Plot, PlotDevice } from "./BokehPlot";

import useDataApi, { Fetch } from "./Fetch";

import "./App.css";

function AppRouter() {
    return (
        <Router>
            <Container fluid className="sticky-top" style={{ padding: 0 }}>
                <Navigation />
                <Container fluid className="border-bottom">
                    <div id="titlebar" className="row">
                        <Switch>
                            <Route path="/about">About</Route>
                            <Route path="/users">Users</Route>
                            <Route path="/plot">Plot</Route>
                            <Route path="/statistics/switch_cycles">On/Off Cycles</Route>
                            <Route path="/database_size">Database Size</Route>
                            <Route path="/">Dashboard</Route>
                        </Switch>
                    </div>
                </Container>
            </Container>
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Container fluid className="p-3">
                <Switch>
                    <Route path="/about">
                        <About />
                    </Route>
                    <Route path="/users">
                        <Users />
                        <Plot src="/backend/test_plot_html" />
                    </Route>
                    <Route path="/plot">
                        <Plot src="/backend/test_plot_html" />
                        <Plot src="/backend/plot_database_size" />
                    </Route>
                    <Route path="/statistics/switch_cycles">
                        <SwitchCycles/>
                    </Route>
                    <Route path="/database_size">
                        <Plot src="/backend/plot_database_size" />
                    </Route>
                    <Route path="/">
                        <Dashboard />
                        <Fetch />
                    </Route>
                </Switch>
            </Container>
        </Router>
    );
}

function ExTable() {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>#</th>
                    <th>First Name</th>
                    <th>Last Name</th>
                    <th>Username</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>Mark</td>
                    <td>Otto</td>
                    <td>@mdo</td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>Jacob</td>
                    <td>Thornton</td>
                    <td>@fat</td>
                </tr>
                <tr>
                    <td>3</td>
                    <td colSpan="2">Larry the Bird</td>
                    <td>@twitter</td>
                </tr>
            </tbody>
        </Table>
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

const App = () => <AppRouter />;

function DashboardOld() {
    return <ExTable />;
}

function Dashboard() {
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}

            {isLoading ? (
                <div>Loading ...</div>
            ) : (
                <Table className={"dataTable"} hover>
                <thead>
                    <tr>
                        <th>Device</th>
                        <th>Device Mode</th>
                        <th>Last Connection</th>
                        <th colSpan={2}>Health Status</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((device) => (
                        <tr key={device}>
                            <th>{device}</th>
                            <DeviceState device_id={device} />
                        </tr>
                    ))}
                </tbody>
            </Table>
            )}
        </>
    );
}

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

const Users = () => <div>There are no users!</div>;

function DeviceState(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(`/backend/device_state/${props.device_id}`, {});

    return (
        <>
            {isError && <div>Something went wrong ...</div>}

            {isLoading ? (
                <>
                    <td></td>
                    <td>Loading ...</td>
                    <td></td>
                    <td></td>
                </>
            ) : (
                <>
                    <td>{data.study_mode}</td>
                    <td>{data.offline_duration}</td>
                    <td>{data.health_status}</td>
                    <td>{data.sick_reason}</td>
                </>
            )}
        </>
    );
}

function SwitchCycles() {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [devices, setDevices] = useState([]);

    useEffect(() => {
        fetch("/backend/devices")
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setDevices(result);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            );
    }, []);

    if (error) {
        return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
        return <div>Loading ...</div>;
    } else {
        return (
            <Table className={"dataTable"} hover>
                <thead>
                    <tr>
                        <th>Device ID</th>
                        <th>Cycles</th>
                        <th>Download</th>
                    </tr>
                </thead>
                <tbody>
                    {devices.map((device) => (
                        <tr key={device}>
                            <th>{device}</th>
                            <td><PlotDevice src={"/backend/plot_switch_cycle"} device={device}/></td>
                            <td><Button>Download</Button></td>
                        </tr>
                    ))}
                </tbody>
            </Table>
        );
    }
}

export default App;
