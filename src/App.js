import React, { Component, useState, useEffect } from "react";

import Jumbotron from "react-bootstrap/Jumbotron";
import Toast from "react-bootstrap/Toast";
import Container from "react-bootstrap/Container";
import Button from "react-bootstrap/Button";
import Alert from "react-bootstrap/Alert";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import Form from "react-bootstrap/Form";
import FormControl from "react-bootstrap/FormControl";
import Table from "react-bootstrap/Table";
import { LinkContainer } from "react-router-bootstrap";

import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import ScriptTag from "react-script-tag";

import "./App.css";

function Navigation() {
    return (
        <Navbar bg="light" expand="lg">
            <Navbar.Brand>REPRO-LIGHT</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <LinkContainer to="/">
                        <Nav.Link>Dashboard</Nav.Link>
                    </LinkContainer>
                    <LinkContainer to="/devices">
                        <Nav.Link>Devices</Nav.Link>
                    </LinkContainer>
                    <LinkContainer to="/about">
                        <Nav.Link>About</Nav.Link>
                    </LinkContainer>
                    <NavDropdown title="Dropdown" id="basic-nav-dropdown">
                        <LinkContainer to="/users">
                            <NavDropdown.Item>Users</NavDropdown.Item>
                        </LinkContainer>
                        <NavDropdown.Item href="/plot">Plot</NavDropdown.Item>
                        <NavDropdown.Divider />
                        <NavDropdown.Item href="/users3">Separated link</NavDropdown.Item>
                    </NavDropdown>
                    <NavDropdown title="Database" id="basic-nav-dropdown">
                        <LinkContainer to="/database_size">
                            <NavDropdown.Item>Size</NavDropdown.Item>
                        </LinkContainer>
                    </NavDropdown>
                </Nav>
                <Form inline>
                    <FormControl type="text" placeholder="Search" className="mr-sm-2" />
                    <Button variant="outline-success">Search</Button>
                </Form>
            </Navbar.Collapse>
        </Navbar>
    );
}

function AppRouter() {
    return (
        <Router>
            <Container fluid className="sticky-top" style={{ padding: 0 }}>
                <Navigation />
                <Container fluid className="border-bottom">
                    <div id="titlebar" className="row">
                        <Switch>
                            <Route path="/about">
                                <h2>About</h2>
                            </Route>
                            <Route path="/devices">
                                <h2>Devices</h2>
                            </Route>
                            <Route path="/users">
                                <h2>Users</h2>
                            </Route>
                            <Route path="/plot">
                                <h2>Plot</h2>
                            </Route>
                            <Route path="/database_size">
                                <h2>Database Size</h2>
                            </Route>
                        </Switch>
                    </div>
                </Container>
            </Container>
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Container className="p-3">
                <Switch>
                    <Route path="/about">
                        <About />
                    </Route>
                    <Route path="/devices">
                        <Devices />
                    </Route>
                    <Route path="/users">
                        <Users />
                    </Route>
                    <Route path="/plot">
                        <Plot />
                    </Route>
                    <Route path="/database_size">
                        <PlotDatabaseSize />
                    </Route>
                    <Route path="/">
                        <Dashboard />
                    </Route>
                </Switch>
            </Container>
        </Router>
    );
}

function Plot() {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [plot_div, setPlotDiv] = useState(null);
    const [plot_script, setPlotScript] = useState(null);

    useEffect(() => {
        const script = document.createElement("script");

        fetch("/backend/test_plot_html")
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setPlotDiv(result.div);
                    setPlotScript(result.script);
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
        console.log(plot_div);
        return (
            <>
                <div dangerouslySetInnerHTML={{ __html: plot_div }}></div>
                <ScriptTag type="text/javascript">{plot_script}</ScriptTag>
            </>
        );
    }
}

function PlotDatabaseSize() {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [plot_div, setPlotDiv] = useState(null);
    const [plot_script, setPlotScript] = useState(null);

    useEffect(() => {
        const script = document.createElement("script");

        fetch("/backend/plot_database_size")
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setPlotDiv(result.div);
                    setPlotScript(result.script);
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
        console.log(plot_div);
        return (
            <>
                <div dangerouslySetInnerHTML={{ __html: plot_div }}></div>
                <ScriptTag type="text/javascript">{plot_script}</ScriptTag>
            </>
        );
    }
}

function ExTable() {
    return (
        <Table striped bordered hover>
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

function Dashboard() {
    return <ExTable />;
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
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [deviceState, setDeviceState] = useState(null);

    useEffect(() => {
        fetch(`/backend/device_state/${props.device_id}`)
            .then((res) => res.json())
            .then(
                (result) => {
                    setIsLoaded(true);
                    setDeviceState(result);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            );
    }, []);

    if (error) {
        return <td>Error: {error.message}</td>;
    } else if (!isLoaded) {
        return <td colSpan={4}>Loading ...</td>;
    } else {
        if (deviceState === null) {
            return <td colSpan={4}>No state</td>;
        } else {
            return (
                <>
                    <td>{deviceState.study_mode}</td>
                    <td>{deviceState.offline_duration}</td>
                    <td>{deviceState.health_status}</td>
                    <td>{deviceState.sick_reason}</td>
                </>
            );
        }
    }
}

function Devices() {
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
            <React.Fragment>
                <h2>Devices</h2>
                <Table striped bordered hover>
                    <thead>
                        <tr>
                            <th>Device</th>
                            <th>Device Mode</th>
                            <th>Last Connection</th>
                            <th colSpan={2}>Health Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {devices.map((device) => (
                            <tr key={device}>
                                <td>{device}</td>
                                <DeviceState device_id={device} />
                            </tr>
                        ))}
                    </tbody>
                </Table>
            </React.Fragment>
        );
    }
}

class DevicesC extends Component {
    constructor(props) {
        super(props);
        this.state = {
            error: null,
            isLoaded: false,
            devices: [],
        };
    }

    componentDidMount() {
        fetch("/backend/devices")
            .then((res) => res.json())
            .then(
                (result) => {
                    this.setState({
                        isLoaded: true,
                        devices: result,
                    });
                },
                // Note: it's important to handle errors here
                // instead of a catch() block so that we don't swallow
                // exceptions from actual bugs in components.
                (error) => {
                    this.setState({
                        isLoaded: true,
                        error,
                    });
                }
            );
    }

    render() {
        const { error, isLoaded, devices } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading ...</div>;
        } else {
            return (
                <React.Fragment>
                    <h2>Devices</h2>
                    <ul>
                        {devices.map((device) => (
                            <li key={device}>{device}</li>
                        ))}
                    </ul>
                </React.Fragment>
            );
        }
    }
}

export default App;
