import React from "react";

import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
//import Form from "react-bootstrap/Form";
//import FormControl from "react-bootstrap/FormControl";
import { LinkContainer } from "react-router-bootstrap";

function Navigation() {
    return (
        <Navbar className="site-header" bg="dark" expand="lg" variant="dark">
            <Navbar.Brand>
                <img src="/ReproLight_trans.png" height="50px" alt="REPRO-LIGHT" />
            </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <LinkContainer to="/">
                        <Nav.Link>Dashboard</Nav.Link>
                    </LinkContainer>
                    <NavDropdown title="Analytics" id="basic-nav-dropdown">
                        <LinkContainer to="/analytics/scenes">
                            <NavDropdown.Item>Scenes</NavDropdown.Item>
                        </LinkContainer>
                        <LinkContainer to="/analytics/connection">
                            <NavDropdown.Item>Connection</NavDropdown.Item>
                        </LinkContainer>
                        <LinkContainer to="/analytics/keyboard">
                            <NavDropdown.Item>Keyboard</NavDropdown.Item>
                        </LinkContainer>
                    </NavDropdown>
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
                    <NavDropdown title="Statistics" id="basic-nav-dropdown">
                        <LinkContainer to="/statistics/switch_cycles">
                            <NavDropdown.Item>On/Off Cycles</NavDropdown.Item>
                        </LinkContainer>
                    </NavDropdown>
                    <NavDropdown title="Database" id="basic-nav-dropdown">
                        <LinkContainer to="/database_size">
                            <NavDropdown.Item>Size</NavDropdown.Item>
                        </LinkContainer>
                    </NavDropdown>
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
