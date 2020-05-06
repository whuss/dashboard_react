import React, { Component, useState } from "react";

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
                        <NavDropdown.Item href="/users2">Something</NavDropdown.Item>
                        <NavDropdown.Divider />
                        <NavDropdown.Item href="/users3">Separated link</NavDropdown.Item>
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
            <Navigation />
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
    return (
        <React.Fragment>
            <h2>Dashboard</h2>
            <ExTable />
        </React.Fragment>
    );
}

function About() {
    return (
        <React.Fragment>
            <h2>About</h2>
            <Jumbotron>
                <h1 className="header">Welcome To React-Bootstrap</h1>
                <ExampleToast>
                    We now have Bootstrap
                    <span role="img" aria-label="tada">
                        🎉
                    </span>
                </ExampleToast>
            </Jumbotron>
        </React.Fragment>
    );
}

const Users = () => <h2>Users</h2>;

class DevicesStatic extends Component {
    state = {
        devices: ["PTL_RD_AT_001", "PTL_RD_AT_002", "PTL_RD_AT_003", "PTL_RD_AT_004"],
    };

    render() {
        return (
            <React.Fragment>
                <h2>Devices</h2>
                <ul>
                    {this.state.devices.map((device) => (
                        <li key={device}>{device}</li>
                    ))}
                </ul>
            </React.Fragment>
        );
    }
}

class Devices extends Component {
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
