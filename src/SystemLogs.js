import React, { Component, useState, useEffect, useRef } from "react";
import ReactDOM from "react-dom";

import { BrowserRouter as Router, Switch, Route, useParams } from "react-router-dom";

import Container from "react-bootstrap/Container";
import ButtonToolbar from "react-bootstrap/ButtonToolbar";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";
import Button from "react-bootstrap/Button";
import { DateTime } from "react-datetime-bootstrap";
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

function logUrl(params) {
    let { device, duration, log_level, timestamp } = params;

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

function DevicePicker(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi("/backend/devices", []);

    const deviceDropdown = (data) => (
        <>
            {data.map((device) => (
                <Dropdown.Item key={device} href={`#${device}`}>
                    {device}
                </Dropdown.Item>
            ))}
        </>
    );

    return (
        <ButtonGroup>
            <span className="label">Device:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={props.device}>
                {isError && <Dropdown.Item>Something went wrong ...</Dropdown.Item>}
                {isLoading ? <Dropdown.Item>Loading...</Dropdown.Item> : deviceDropdown(data)}
            </DropdownButton>
        </ButtonGroup>
    );
}

function LogLevelPicker(props) {
    const log_levels = ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

    const log_span = (level) => <span className={level}>{level}</span>;

    return (
        <ButtonGroup>
            <span className="label">Logging&nbsp;level:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={log_span(props.log_level)}>
                {log_levels.map((level) => (
                    <Dropdown.Item key={level}>{log_span(level)}</Dropdown.Item>
                ))}
            </DropdownButton>
        </ButtonGroup>
    );
}

function DateTimeInput(props) {
    return (
        <ButtonGroup>
            <ButtonGroup>
                <span className="label">At&nbsp;time:</span>
                <InputGroup className="mb-2">
                    <FormControl value={props.timestamp} />
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

function DurationPicker(props) {
    return (
        <ButtonGroup>
            <span className="label">Duration:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={props.duration}>
                <Dropdown.Item href="#/action-1">1 Minute</Dropdown.Item>
                <Dropdown.Item href="#/action-2">5 Minutes</Dropdown.Item>
                <Dropdown.Item href="#/action-3">10 Minutes</Dropdown.Item>
            </DropdownButton>
        </ButtonGroup>
    );
}

function LogToolbar() {
    let { device, duration, log_level, timestamp } = useParams();
    return (
        <Container id="toolbar">
            <ButtonToolbar>
                <DevicePicker device={device} />
                <LogLevelPicker log_level={log_level} />
                <DateTimeInput timestamp={timestamp} />
                <DurationPicker duration={duration} />
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

    const url = logUrl(useParams());

    return (
        <>
            <Toolbar>
                <LogToolbar />
            </Toolbar>
            <ul>
                <li>device: {device}</li>
                <li>duration: {duration}</li>
                <li>level: {log_level}</li>
                <li>timestamp: {timestamp}</li>
            </ul>
            <span>{url}</span>
            <div>Logs</div>
            <FetchLogs url={url} />
        </>
    );
}

export default SystemLogs;
