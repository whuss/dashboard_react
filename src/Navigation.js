import React from "react";

import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
//import Form from "react-bootstrap/Form";
//import FormControl from "react-bootstrap/FormControl";
import { LinkContainer } from "react-router-bootstrap";

function NavDropLink(props) {
    return <LinkContainer to={props.to}><NavDropdown.Item>{props.name}</NavDropdown.Item></LinkContainer>
}

function NavLink(props) {
    return <LinkContainer to={props.to}><Nav.Link>{props.name}</Nav.Link></LinkContainer>
}

function Navigation() {
    return (
        <Navbar className="site-header" bg="dark" expand="lg" variant="dark">
            <Navbar.Brand>
                <img src="/ReproLight_trans.png" height="50px" alt="REPRO-LIGHT" />
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                <NavLink to="/" name="Dashboard" />
                    <NavDropdown title="Analytics" id="basic-nav-dropdown">
                        <NavDropLink to="/analytics/scenes" name="Scenes"/>
                        <NavDropLink to="/analytics/connection" name="Connection"/>
                        <NavDropLink to="/analytics/keyboard" name="Keyboard"/>
                        <NavDropdown.Divider />
                    </NavDropdown>
                    <NavDropdown title="Statistics" id="basic-nav-dropdown">
                        <NavDropLink to="/statistics/switch_cycles" name="On/Off Cycles"/>
                    </NavDropdown>
                    <NavDropdown title="System" id="basic-nav-dropdown">
                        <NavDropLink to="/system/stability" name="Stability"/>
                        <NavDropLink to="/system/restarts" name="Restarts"/>
                    </NavDropdown>
                    <NavDropdown title="Database" id="basic-nav-dropdown">
                        <NavDropLink to="/database_size" name="Size"/>
                    </NavDropdown>
                    <NavLink to="/about" name="About" />
                </Nav>
                {/* <Form inline>
                    <FormControl type="text" placeholder="Search" className="mr-sm-2" />
                    <Button>Search</Button>
                </Form> */}
            </Navbar.Collapse>
            <Navbar.Brand>
                <img src="/dot_bartenbach.png" height="50px" alt="Bartenbach" />
            </Navbar.Brand>
        </Navbar>
    );
}

export default Navigation;
