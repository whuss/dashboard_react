import React, { useState } from "react";

import { usePlot } from "./BokehPlot";

import Col from "react-bootstrap/Col";

import Toolbar, { useDeviceDropdown, LoadingAnimation } from "./Toolbar";

import { useParams } from "react-router-dom";

import Row from "react-bootstrap/Row";
import ListGroup from "react-bootstrap/ListGroup";

const queries = [
    { name: "Analytics|Power", selected: false, view: "PlotPowerTimeline" },
    { name: "Analytics|Scenes", selected: false, view: "PlotSceneDurations" },
    { name: "Analytics|Connection", selected: false, view: "PlotConnection" },
    { name: "Analytics|Keyboard", selected: false, view: "PlotKeyboard" },
    { name: "Analytics|Mouse", selected: false, view: "PlotMouse" },
    { name: "Clustering|Daily Frequency", selected: false, view: "PlotClusteringFrequency" },
    { name: "Clustering|Daily Timeline", selected: false, view: "PlotClusteringTimeline" },
];

const keys = [...Array(7).keys()];

function useSidebar() {
    const [state, setState] = useState([false, false, false, false, false, false, false]);

    const selected = (key) => {
        if (state[key]) {
            return "primary";
        }
        return "";
    };

    const toggleSelection = (key) => {
        console.log("toggleSelection: ", key);
        console.log("state:", state);
        var newState = [...state];
        newState[key] = !state[key];
        console.log("new state: ", newState);
        setState(newState);
    };

    const Sidebar = () => (
        <div className="sidebar-sticky">
            <ListGroup>
                {keys.map((key) => (
                    <ListGroup.Item action key={key} variant={selected(key)} onClick={() => toggleSelection(key)}>
                        {queries[key].name}
                    </ListGroup.Item>
                ))}
            </ListGroup>
        </div>
    );

    return [state, Sidebar];
}

function useToolbar(_device, devices) {
    if (!_device) {
        _device = devices[0];
    }

    const [device, setDevice] = useDeviceDropdown(_device, devices);

    const logToolbar = <>{setDevice}</>;

    return [device, logToolbar];
}

const NamedPlot = (props) => {
    const plot_name = props.plot_name;
    const plot_parameters = { device: props.device };
    const [{ isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters, false);

    return (
        <>
            <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                {plot}
            </LoadingAnimation>
        </>
    );
};

function renderDetails(device, key, selected) {
    const plot_name = queries[key].view;
    if (selected) {
        return <NamedPlot key={plot_name} plot_name={plot_name} device={device} />;
    }
}

const DeviceDetails = (props) => {
    let params = useParams();

    const [device, toolbar] = useToolbar(params.device, props.devices);

    const [state, Sidebar] = useSidebar();

    return (
        <>
            <Toolbar>{toolbar}</Toolbar>
            <Row>
                <Col xs={3} id="sidebar-wrapper">
                    <Sidebar />
                </Col>
                <Col xs={9} id="page-content-wrapper">
                    <ul>{keys.map((key) => renderDetails(device, key, state[key]))}</ul>
                </Col>
            </Row>
        </>
    );
};

export default DeviceDetails;
