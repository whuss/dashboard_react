import React, { Component, useState, useEffect, useRef } from "react";

import { BrowserRouter as Router, Switch, Route, useParams} from "react-router-dom";

import useDataApi from "./Fetch";

function Logs(props) {
    const [{ data, isLoading, isError }, doFetch] = useDataApi(props.url, []);

    return (
        <>
            {isError && <div>Something went wrong ...</div>}
            {isLoading ? <div>Loading ...</div> : <pre dangerouslySetInnerHTML={{ __html: data.log_text}}/>}
        </>
    );
}

function SystemLogs() {
    let {device, duration, log_level, timestamp } = useParams();

    const url = `/backend/logs/${device}/${duration}/${log_level}/${timestamp}`;

    return (
        <>
        <ul>
            <li>device: {device}</li>
            <li>duration: {duration}</li>
            <li>level: {log_level}</li>
            <li>timestamp: {timestamp}</li>
        </ul>
        <div>Logs</div>
        <Logs url={url}/>
        </>
    )
}

export default SystemLogs;
