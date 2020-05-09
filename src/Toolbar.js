import React, { useEffect, useState } from "react";
import ReactDOM from "react-dom";

import Container from "react-bootstrap/Container";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";

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

function useDeviceFilter(initialValue) {
    const [{ data, isLoading, isError }] = useDataApi("/backend/devices", []);
    const devices = data;

    const [filterStr, setFilterStr] = useInput(initialValue ? initialValue : useDeviceFilter.filter, {
        prepend: (
            <>
                <i className="fa fa-lightbulb-o" aria-hidden="true"></i>
                <span className="label">Filter:</span>
            </>
        ),
    });

    useEffect(() => {
        useDeviceFilter.filter = filterStr;
    }, [filterStr]);

    const selectedDevices = devices.filter((s) => s.includes(filterStr));

    const deviceFilter = (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <Spinner animation="border" size="sm" variant="secondary" /> : setFilterStr}
        </>
    );

    return [selectedDevices, deviceFilter];
}
useDeviceFilter.filter = "";

function useDropdown(initialValue, config) {
    let { values, label, format } = config;

    if (!format) {
        format = (value) => value;
    }

    const [value, setValue] = useState(initialValue);

    const dropdown = (
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
    );

    return [value, dropdown];
}

function useDevice(device) {
    const [{ data, isLoading, isError }] = useDataApi("/backend/devices", []);
    const devices = data;

    const [selectedDevice, dropdown] = useDropdown(device, {
        values: devices,
        label: "Device",
    });

    const deviceDropdown = (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <Spinner animation="border" size="sm" variant="secondary" /> : dropdown}
        </>
    );

    return [selectedDevice, deviceDropdown];
}

function useTimestamp(_timestamp) {
    const [timestamp, setTimestamp] = useState(_timestamp);
    const datetimeSelector = (
        <ButtonGroup>
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
        </ButtonGroup>
    );

    return [timestamp, datetimeSelector];
}

function Toolbar(props) {
    const toolBarRoot = document.getElementById("toolbar-root");

    const toolBar = <Container id="toolbar">{props.children}</Container>;

    return ReactDOM.createPortal(toolBar, toolBarRoot);
}

export default Toolbar;
export { useInput, useDeviceFilter, useDropdown, useDevice, useTimestamp };
