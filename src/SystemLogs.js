import React, { useState, useEffect } from "react";

import moment from "moment";

import { useParams } from "react-router-dom";

import useDataApi from "./Fetch";
import Toolbar, { useDropdown, useDeviceDropdown, useTimestamp, LoadingAnimation } from "./Toolbar";

function useLog(url) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(url, []);

    useEffect(() => {
        doFetch(url);
    });

    const logText = <pre dangerouslySetInnerHTML={{ __html: data.log_text }} />;

    return <LoadingAnimation isLoading={isLoading} isError={isError}>{logText}</LoadingAnimation>;
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

function formatDuration(duration) {
    if (duration === 60) {
        return "1 hour";
    }
    if (duration > 60) {
        return `${duration/60} hours`;
    }
    return `${duration} minutes`;
}

function useLogToolbar(_device, _duration, _log_level, _timestamp, devices) {
    if (!_device)
    {
        _device = devices[0];
    }
    if (!_duration) {
        _duration = 5;
    }
    if (!_log_level) {
        _log_level = "DEBUG";
    }
    if (!_timestamp) {
        _timestamp = moment().subtract(5, 'minutes').format('YYYY-MM-DD hh:mm:ss');
    }

    const [device, setDevice] = useDeviceDropdown(_device, devices);
    const [log_level, setLogLevel] = useDropdown(_log_level, {
        label: "Logging level",
        values: ["TRACE", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        format: (level) => <span className={level}>{level}</span>,
    });
    const [timestamp, setTimestamp] = useTimestamp(_timestamp);
    const [duration, setDuration] = useDropdown(_duration, {
        label: "Duration",
        values: [5, 10, 30, 60, 12*60, 24*60],
        format: (duration) => <span>{formatDuration(duration)}</span>
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

function SystemLogs(props) {
    let params = useParams();

    const [{ device, log_level, timestamp, duration }, logToolbar] = useLogToolbar(
        params.device,
        params.duration,
        params.log_level,
        params.timestamp,
        props.devices
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
