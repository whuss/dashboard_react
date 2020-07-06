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
                    <NavDropdown title="Plots" id="basic-nav-dropdown">
                        <NavDropLink to="/plots/bokeh" name="Bokeh" />
                        <NavDropdown.Divider />
                        <NavDropLink to="/plots/matplotlib" name="Matplotlib" />
                        <NavDropLink to="/plots/chartjs" name="ChartJS" />
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