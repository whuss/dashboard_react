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
import Dashboard from "./Dashboard";
import SwitchCycles from "./SwitchCycles";
import { Plot, PlotDevice } from "./BokehPlot";

import useDataApi, { FetchHackernews } from "./Fetch";

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
                        <FetchHackernews />
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

const App = () => <AppRouter />;

export default App;
