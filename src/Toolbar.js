import React, { useState } from "react";
import ReactDOM from "react-dom";

import Container from "react-bootstrap/Container";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";

import useDataApi from "./Fetch";

function useDeviceOld(device) {
    const [_device, setDevice] = useState(device);
    const [{ data, isLoading, isError }] = useDataApi("/backend/devices", []);

    const deviceDropdown = (data) => (
        <>
            {data.map((_device) => (
                <Dropdown.Item key={_device} onSelect={() => setDevice(_device)}>
                    {_device}
                </Dropdown.Item>
            ))}
        </>
    );

    const devicePicker = (
        <ButtonGroup>
            <span className="label">Device:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={_device}>
                {isError && <Dropdown.Item>Something went wrong ...</Dropdown.Item>}
                {isLoading ? <Dropdown.Item>Loading...</Dropdown.Item> : deviceDropdown(data)}
            </DropdownButton>
        </ButtonGroup>
    );

    return [_device, devicePicker];
}

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

function useDevice(device, all) {
    const [{ data, isLoading, isError }] = useDataApi("/backend/devices", []);

    const devices = all ? ["ALL"].concat(data) : data;

    return useDropdown(device, {
        values: devices,
        label: "Device",
    });
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
export { useDropdown, useDevice, useTimestamp };
