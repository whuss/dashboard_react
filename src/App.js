import React from "react";
import Container from "react-bootstrap/Container";
import Jumbotron from "react-bootstrap/Jumbotron";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";

import "./App.css";
import Dashboard from "./dashboard/Dashboard";
import Navigation from "./Navigation";
import ExamplePlotBokeh from "./examplePlots/Bokeh";
import ExamplePlotMatplotlib from "./examplePlots/Matplotlib";
import ExamplePlotChartJs from "./examplePlots/ChartJS";

const Title = (props) => {
    const titleBar = document.getElementById("titlebar-root");
    return ReactDOM.createPortal(<h2>{props.title}</h2>, titleBar);
};

const NavPortal = () => {
    const titleBar = document.getElementById("navbar-root");
    return ReactDOM.createPortal(<Navigation />, titleBar);
};

const NavRoute = ({ path, title, children }) => (
    <Route path={path}>
        <Title title={title} />
        {children}
    </Route>
);

const About = () => (
    <>
        <Jumbotron>
            <h1 className="header">Todo ...</h1>
        </Jumbotron>
    </>
);

const MainView = () => {
    return (
        <Container fluid>
            {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
            <Switch>
                <NavRoute path="/about" title="About">
                    <About />
                </NavRoute>
                <NavRoute path="/plots/bokeh" title="Bokeh Plot">
                    <ExamplePlotBokeh />
                </NavRoute>
                <NavRoute path="/plots/matplotlib" title="Matplotlib Plot">
                    <ExamplePlotMatplotlib />
                </NavRoute>
                <NavRoute path="/plots/chartjs" title="ChartJS Plot">
                    <ExamplePlotChartJs />
                </NavRoute>
                <NavRoute path="/" title="Field study fact sheet (work in progress)">
                    <Dashboard />
                </NavRoute>
            </Switch>
        </Container>
    );
};

const App = () => {
    return (
        <Router>
            <NavPortal />
            <MainView />
        </Router>
    );
};

export default App;
