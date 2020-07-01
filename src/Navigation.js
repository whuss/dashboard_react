import React from "react";

import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
import { LinkContainer } from "react-router-bootstrap";

function NavDropLink(props) {
    return (
        <LinkContainer to={props.to}>
            <NavDropdown.Item>{props.name}</NavDropdown.Item>
        </LinkContainer>
    );
}

function NavLink(props) {
    return (
        <LinkContainer to={props.to}>
            <Nav.Link>{props.name}</Nav.Link>
        </LinkContainer>
    );
}

function Navigation() {
    return (
        <Navbar className="site-header" bg="dark" expand="lg" variant="dark">
            <Navbar.Brand>
                <a href="https://www.repro-light.eu"><img src="/ReproLight_trans.png" height="50px" alt="REPRO-LIGHT" /></a>
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <NavLink to="/" name="Dashboard" />
                    <NavDropdown title="Analytics" id="basic-nav-dropdown">
                        <NavDropLink to="/analytics/sensor" name="Sensor" />
                        <NavDropdown.Divider />
                        <NavDropLink to="/analytics/settings" name="Settings" />
                        <NavDropLink to="/analytics/power" name="Power timeline" />
                        <NavDropLink to="/statistics/switch_cycles" name="On/Off Cycles" />
                        <NavDropLink to="/analytics/scenes" name="Scenes" />
                        <NavDropLink to="/analytics/connection" name="Connection" />
                        <NavDropdown.Divider />
                        <NavDropLink to="/analytics/keyboard" name="Keyboard" />
                        <NavDropLink to="/analytics/keypress" name="Keypress" />
                        <NavDropLink to="/analytics/mouse" name="Mouse" />
                        <NavDropdown.Divider />
                        <NavDropLink to="/analytics/gaze" name="Gaze" />
                    </NavDropdown>
                    <NavDropdown title="Clustering" id="basic-nav-dropdown">
                        <NavDropLink to="/clustering/input_distributions" name="Input Distributions" />
                        <NavDropLink to="/clustering/scatter_plot" name="Cluster Scatter Plot" />
                        <NavDropLink to="/clustering/frequency" name="Daily Cluster Frequency" />
                        <NavDropLink to="/clustering/timeline" name="Daily Cluster Timeline" />
                    </NavDropdown>
                    <NavDropdown title="System" id="basic-nav-dropdown">
                        <NavDropLink to="/system/stability" name="Stability" />
                        <NavDropLink to="/system/restarts" name="Restarts" />
                        <NavDropLink to="/system/errors" name="Errors" />
                        <NavDropLink to="/system/device_status" name="Device Status" />    
                        <NavDropLink to="/database_size" name="Database Size" />
                        <NavDropdown.Divider />
                        <NavDropLink to="/logs" name="Logs" />
                    </NavDropdown>
                    <NavLink to="/about" name="About" />
                </Nav>
            </Navbar.Collapse>
            <Navbar.Brand>
                <a href="https://www.bartenbach.com"><img src="/dot_bartenbach.png" height="50px" alt="Bartenbach" /></a>
            </Navbar.Brand>
        </Navbar>
    );
}

export default Navigation;
export { NavLink };