import React, { useState, useEffect } from "react";

import Spinner from "react-bootstrap/Spinner";

import { useParams } from "react-router-dom";

import useDataApi from "./Fetch";
import Toolbar, { useDropdown, useDevice, useTimestamp } from "./Toolbar";

function useLog(url) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(url, []);

    useEffect(() => {
        doFetch(url);
    });

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <Spinner animation="border" size="sm" variant="secondary" /> : <pre dangerouslySetInnerHTML={{ __html: data.log_text }} />}
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

function useLogToolbar(_device, _duration, _log_level, _timestamp) {
    const [device, setDevice] = useDevice(_device);
    const [log_level, setLogLevel] = useDropdown(_log_level, {
        label: "Logging level",
        values: ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        format: (level) => <span className={level}>{level}</span>,
    });
    const [timestamp, setTimestamp] = useTimestamp(_timestamp);
    const [duration, setDuration] = useDropdown(_duration, {
        label: "Duration",
        values: [1, 5, 10, 30],
        format: (duration) => <span>{duration} Minutes</span>
    });

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
