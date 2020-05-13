import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";

import Container from "react-bootstrap/Container";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";
import Row from 'react-bootstrap/Row'
import Col from 'react-bootstrap/Col'
import Spinner from "react-bootstrap/Spinner";

import useDataApi from "./Fetch";

function useInput(_value, config) {
    const { label, prepend, append } = config;
    const [value, setValue] = useState(_value);
    const inputField = (
        <ButtonGroup>
            {label && <span className="label">{label}</span>}
            <InputGroup className="mb-1">
                {prepend && (
                    <InputGroup.Prepend>
                        <InputGroup.Text>{prepend}</InputGroup.Text>
                    </InputGroup.Prepend>
                )}
                <FormControl defaultValue={value} onChange={(e) => setValue(e.target.value)} />
                {append && (
                    <InputGroup.Append>
                        <InputGroup.Text>{append}</InputGroup.Text>
                    </InputGroup.Append>
                )}
            </InputGroup>
        </ButtonGroup>
    );

    return [value, inputField];
}

function useDropdown(initialValue, config) {
    let { values, label, format } = config;

    if (!format) {
        format = (value) => value;
    }

    const [value, setValue] = useState(initialValue);

    const dropdown = (
        <>
        <ButtonGroup>
            {label && <span className="label">{label}:</span>}
            <DropdownButton id="dropdown-basic-button" variant="light" title={format(value)}>
                {values.map((v) => (
                    <Dropdown.Item key={v} onSelect={() => setValue(v)}>
                        {format(v)}
                    </Dropdown.Item>
                ))}
            </DropdownButton>
        </ButtonGroup>
        </>
    );

    return [value, dropdown];
}

const LoadingAnimation = (props) => {
    const spinner = props.spinner ? <></> : <div style={props.style}><Spinner animation="border" size="sm" variant="secondary" /></div>; 
    const use_spinner = props.silent ? <></> : spinner;

    return (
        <>
            {props.isError && <div>Something went wrong ...</div>}
            {props.isLoading ? use_spinner : props.children}
        </>
    );
};

function useDevice() {
    const [{ data, isLoading, isError }] = useDataApi("/backend/devices", []);
    const devices = data;

    return [devices, isLoading, isError];
}

function useDeviceFilter(initialValue, devices) {
    const [filterStr, deviceFilter] = useInput(initialValue ? initialValue : useDeviceFilter.filter, {
        prepend: (
            <>
                <i className="fa fa-lightbulb-o" aria-hidden="true"></i>
                <span className="label">&nbsp;Filter:</span>
            </>
        ),
    });

    useEffect(() => {
        useDeviceFilter.filter = filterStr;
    }, [filterStr]);

    const selectedDevices = devices.filter((s) => s.includes(filterStr));

    return [selectedDevices, deviceFilter];
}
useDeviceFilter.filter = "";

function useFilter(initialValue, config) {
    let { values, label } = config;
    const [filterStr, valueFilter] = useInput(initialValue, {
        prepend: (
            <>
                {label && <span className="label">{label}</span>}
            </>
        ),
    });

    const selectedValues = values.filter((s) => s.includes(filterStr));

    return [selectedValues, valueFilter];
}


function useDeviceDropdown(device, devices) {
    const [selectedDevice, deviceDropdown] = useDropdown(device, {
        values: devices,
        label: "Device",
    });

    return [selectedDevice, deviceDropdown];
}

function useTimestamp(_timestamp) {
    const [timestamp, setTimestamp] = useState(_timestamp);
    const datetimeSelector = (
            <ButtonGroup>
                <span className="label">At&nbsp;time:</span>
                <InputGroup className="mb-2">
                    <FormControl defaultValue={timestamp} onChange={(e) => setTimestamp(e.target.value)} />
                    <InputGroup.Append>
                        <InputGroup.Text id="basic-addon2">
                            <i className="fa fa-calendar" aria-hidden="true"></i>
                        </InputGroup.Text>
                    </InputGroup.Append>
                </InputGroup>
            </ButtonGroup>
    );

    return [timestamp, datetimeSelector];
}

function Toolbar(props) {
    const toolBarRoot = document.getElementById("toolbar-root");

    const toolBar = <Container fluid id="toolbar"><Row lg={12}>{props.children}</Row></Container>;

    return ReactDOM.createPortal(toolBar, toolBarRoot);
}

export default Toolbar;
export { useInput, useDeviceFilter, useDropdown, useDeviceDropdown, useTimestamp, LoadingAnimation, useDevice, useFilter };
