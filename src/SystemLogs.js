import React, { useState, useEffect } from "react";

import moment from "moment";

import queryString from 'query-string';

import { useParams, useLocation, useHistory } from "react-router-dom";

import useDataApi from "./Fetch";
import Toolbar, { ToolbarBottom, useDropdown, useDeviceDropdown, useTimestamp, LoadingAnimation } from "./Toolbar";

import Container from "react-bootstrap/Container";

import PaginationBar from "./PaginationBar";

function useLog(url) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(url, []);

    useEffect(() => {
        doFetch(url);
    });

    const logText = <pre dangerouslySetInnerHTML={{ __html: data.log_text }} />;

    return [
        data && data.pagination,
        <LoadingAnimation isLoading={isLoading} isError={isError}>
            {logText}
        </LoadingAnimation>,
    ];
}

function logUrl(device, duration, log_level, timestamp, query_params) {
    const baseUrl = "/logs";

    const params = new URLSearchParams(query_params);

    if (timestamp) {
        return `${baseUrl}/${device}/${duration}/${log_level}/${timestamp}?${params.toString()}`;
    }
    if (log_level) {
        return `${baseUrl}/${device}/${duration}/${log_level}?${params.toString()}`;
    }
    if (duration) {
        return `${baseUrl}/${device}/${duration}?${params.toString()}`;
    }
    if (device) {
        return `${baseUrl}/${device}?${params.toString()}`;
    }

    return baseUrl;
}

function formatDuration(duration) {
    if (duration === 60) {
        return "1 hour";
    }
    if (duration > 60) {
        return `${duration / 60} hours`;
    }
    return `${duration} minutes`;
}

function useLogToolbar(_device, _duration, _log_level, _timestamp, devices) {
    if (!_device) {
        _device = devices[0];
    }
    if (!_duration) {
        _duration = 5;
    }
    if (!_log_level) {
        _log_level = "DEBUG";
    }
    if (!_timestamp) {
        _timestamp = moment().subtract(5, "minutes").format("YYYY-MM-DD hh:mm:ss");
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
        values: [5, 10, 30, 60, 12 * 60, 24 * 60],
        format: (duration) => <span>{formatDuration(duration)}</span>,
    });

    const logToolbar = (pagination) => (
        <>
            {setDevice}
            {setLogLevel}
            {setTimestamp}
            {setDuration}
            {pagination}
        </>
    );

    return [{ device, log_level, timestamp, duration }, logToolbar];
}

function SystemLogs(props) {
    let history = useHistory();
    let params = useParams();
    let search = queryString.parse(useLocation().search);

    const [page, setPage ] = useState(1);

    const query_params = {...search, page: page};

    const [{ device, log_level, timestamp, duration }, logToolbar] = useLogToolbar(
        params.device,
        params.duration,
        params.log_level,
        params.timestamp,
        props.devices
    );

    const thisPageUrl = logUrl(device, duration, log_level, timestamp, query_params);

    const [url, setUrl] = useState(thisPageUrl);

    const [paginationData, logText] = useLog(url);

    const paginationElement = <Container fluid className="d-flex justify-content-end"><PaginationBar setPage={setPage} pagination={paginationData}/></Container>;

    useEffect(() => {
        setPage(1);
    }, [device, log_level, timestamp, duration]);

    useEffect(() => {
        const newUrl = '/backend' + thisPageUrl;
        setUrl(newUrl);
    }, [device, log_level, timestamp, duration, search]);

    useEffect(() => {
        history.replace(thisPageUrl);
    }, [thisPageUrl]);

    return (
        <>
            <Toolbar>{logToolbar(paginationElement)}</Toolbar>
            {logText}
            {paginationData && paginationData.num_pages > 1 && <ToolbarBottom><Container fluid className="d-flex justify-content-end">{paginationElement}</Container></ToolbarBottom>}
        </>
    );
}

export default SystemLogs;
