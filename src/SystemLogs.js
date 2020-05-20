import React, { useState, useEffect } from "react";

import moment from "moment";

import { useParams } from "react-router-dom";

import useDataApi from "./Fetch";
import Toolbar, { useDropdown, useDeviceDropdown, useTimestamp, LoadingAnimation } from "./Toolbar";

import Pagination from "react-bootstrap/Pagination";
import PageItem from "react-bootstrap/PageItem";

function PaginationBar(props) {
    const pagination = props.pagination;
    const setPage = props.setPage;

    if (!pagination) {
        return <><span>Pagination undefined</span></>;
    }

    const { current_page, num_pages, has_next, has_prev, next_num, prev_num, pages } = pagination;

    if (num_pages === 1) {
        return <>Num pages 1</>;
    }

    function clickPage(page) {
        console.log("click page: ", page);
        setPage(page);
    }

    function prevPage() {
        console.log("prev page");
        if (has_prev) {
            setPage(current_page - 1);
        }
    }

    function nextPage() {
        console.log("next page");
        if (has_next) {
            setPage(current_page + 1);
        }
    }

    function item(page) {
        if (page) {
            return (
                <Pagination.Item onClick={() => clickPage(page)} key={page} active={page === current_page}>
                    {page}
                </Pagination.Item>
            );
        }
        return (
            <Pagination.Item key="ellipsis" disabled={true} active={false}>
                &hellip;
            </Pagination.Item>
        );
    }

    return (
        <Pagination>
            <Pagination.Prev  onClick={() => prevPage()} disabled={!has_prev} />
            {pages.map((page) => item(page))}
            <Pagination.Next onClick={() => nextPage()} disabled={!has_next} />
        </Pagination>
    );
}

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

function logUrl(device, duration, log_level, timestamp, page) {
    const baseUrl = "/backend/logs";

    if (page === undefined)
    {
        page = 1;
    }

    const params = new URLSearchParams({
        page: page,
    });

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
    let params = useParams();

    const [page, setPage ] = useState(1);

    const [{ device, log_level, timestamp, duration }, logToolbar] = useLogToolbar(
        params.device,
        params.duration,
        params.log_level,
        params.timestamp,
        props.devices
    );

    const [url, setUrl] = useState(logUrl(device, duration, log_level, timestamp, page));

    const [paginationData, logText] = useLog(url);

    const paginationElement = <PaginationBar setPage={setPage} pagination={paginationData}/>;

    useEffect(() => {
        const newUrl = logUrl(device, duration, log_level, timestamp, page);
        setUrl(newUrl);
        //props.history.push(newUrl);
    }, [device, log_level, timestamp, duration, page]);

    return (
        <>
            <Toolbar>{logToolbar(paginationElement)}</Toolbar>
            <div>Current page: {page}</div>
            {logText}
        </>
    );
}

export default SystemLogs;
