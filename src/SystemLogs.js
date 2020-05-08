import React, { Component, useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom";

import { BrowserRouter as Router, Switch, Route, useParams } from "react-router-dom";

import Container from "react-bootstrap/Container";
import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import Button from "react-bootstrap/Button";
import InputGroup from "react-bootstrap/InputGroup";
import FormControl from "react-bootstrap/FormControl";

import useDataApi from "./Fetch";

function FetchLogs(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(props.url, []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <div>Loading ...</div> : <pre dangerouslySetInnerHTML={{ __html: data.log_text }} />}
        </>
    );
}

function logUrl(device, duration, log_level, timestamp) {
    const baseUrl = "/backend/logs";

    if (timestamp) {
        return `${baseUrl}/${device}/${duration}/${log_level}/${timestamp}`;
    }
    if (log_level) {
        return `${baseUrl}/${device}/${duration}/${log_level}`;
    }
    if (duration) {
        return `${baseUrl}/${device}/${duration}`;
    }
    if (device) {
        return `${baseUrl}/${device}`;
    }
    return baseUrl;
}


function useDevice(device) {
    const [_device, setDevice] = useState(device);
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);

    const deviceDropdown = (data) => (
        <>
            {data.map((_device) => (
                <Dropdown.Item key={_device} href={`#${_device}`} onSelect={() => setDevice(_device)}>
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

function useLogLevel(level) {
    const [log_level, setLogLevel] = useState(level);
    const log_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

    const log_span = (level) => <span className={level}>{level}</span>;
    const logLevelPicker = (
        <ButtonGroup>
            <span className="label">Logging&nbsp;level:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={log_span(log_level)}>
                {log_levels.map((level) => (
                    <Dropdown.Item key={level} onSelect={() => setLogLevel(level)}>
                        {log_span(level)}
                    </Dropdown.Item>
                ))}
            </DropdownButton>
        </ButtonGroup>
    );

    return [log_level, logLevelPicker];
}

function DateTimeInput(props) {
    const [timestamp, setTimestamp] = useState(props.timestamp);
    return (
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
}

function useDuration(_duration) {
    const [duration, setDuration] = useState(_duration);
    const durations = [1, 5, 10, 30];

    const durationPicker = (
        <ButtonGroup>
            <span className="label">Duration:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={duration}>
                {durations.map((duration) => (
                    <Dropdown.Item key={duration} onSelect={() => setDuration(duration)}>
                        <span>{duration} Minutes</span>
                    </Dropdown.Item>
                ))}
            </DropdownButton>
        </ButtonGroup>
    );

    return [duration, durationPicker];
}


function LogToolbar(props) {
    return (
        <Container id="toolbar">
            <ButtonToolbar>
            </ButtonToolbar>
        </Container>
    );
}

function Toolbar(props) {
    const toolBar = document.getElementById("toolbar-root");
    return ReactDOM.createPortal(props.children, toolBar);
}

function SystemLogs() {
    let { device, duration, log_level, timestamp } = useParams();

    const [_timestamp, setTimestamp] = useState(timestamp);

    const [_log_level, setLogLevel] = useLogLevel(log_level);
    const [_device, setDevice] = useDevice(device);
    const [_duration, setDuration] = useDuration(duration);

    const url = logUrl(_device, _duration, _log_level, _timestamp);

    return (
        <>
            <Toolbar>
                {/* <LogToolbar device={_device} duration={_duration} log_level={_log_level} timestamp={_timestamp} /> */}
                <Container id="toolbar">
                    <ButtonToolbar>
                        {setDevice}
                        {setLogLevel}
                        <DateTimeInput timestamp={_timestamp} />
                        {setDuration}
                    </ButtonToolbar>
                </Container>
            </Toolbar>
            <ul>
                <li>device: {_device}</li>
                <li>duration: {_duration}</li>
                <li>level: {_log_level}</li>
                <li>timestamp: {_timestamp}</li>
            </ul>
            <span>{url}</span>
            <div>Logs</div>
            <FetchLogs url={url} />
        </>
    );
}

export default SystemLogs;
