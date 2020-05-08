import React, { useState, useEffect } from "react";

import { useParams } from "react-router-dom";

import ButtonGroup from "react-bootstrap/ButtonGroup";
import Dropdown from "react-bootstrap/Dropdown";
import DropdownButton from "react-bootstrap/DropdownButton";

import useDataApi from "./Fetch";
import Toolbar, { useDevice, useTimestamp } from "./Toolbar";

function useLog(url) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(url, []);

    useEffect(() => {
        doFetch(url);
    });

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

function useDuration(_duration) {
    const [duration, setDuration] = useState(_duration);
    const durations = [1, 5, 10, 30];

    const durationSpan = (duration) => <span>{duration} Minutes</span>;

    const durationPicker = (
        <ButtonGroup>
            <span className="label">Duration:</span>
            <DropdownButton id="dropdown-basic-button" variant="light" title={durationSpan(duration)}>
                {durations.map((duration) => (
                    <Dropdown.Item key={duration} onSelect={() => setDuration(duration)}>
                        {durationSpan(duration)}
                    </Dropdown.Item>
                ))}
            </DropdownButton>
        </ButtonGroup>
    );

    return [duration, durationPicker];
}

function useLogToolbar(_device, _duration, _log_level, _timestamp) {
    const [device, setDevice] = useDevice(_device);
    const [log_level, setLogLevel] = useLogLevel(_log_level);
    const [timestamp, setTimestamp] = useTimestamp(_timestamp);
    const [duration, setDuration] = useDuration(_duration);

    const logToolbar = (
        <>
            {setDevice}
            {setLogLevel}
            {setTimestamp}
            {setDuration}
        </>
    );

    return [{ device, log_level, timestamp, duration }, logToolbar];
}

function SystemLogs() {
    let params = useParams();

    const [{ device, log_level, timestamp, duration }, logToolbar] = useLogToolbar(
        params.device,
        params.duration,
        params.log_level,
        params.timestamp
    );

    const [url, setUrl] = useState(logUrl(device, duration, log_level, timestamp));

    const logText = useLog(url);

    useEffect(() => {
        const newUrl = logUrl(device, duration, log_level, timestamp);
        setUrl(newUrl);
        //props.history.push(newUrl);
    }, [device, log_level, timestamp, duration]);

    return (
        <>
            <Toolbar>{logToolbar}</Toolbar>
            {logText}
        </>
    );
}

export default SystemLogs;
