import React, { useState, useEffect } from "react";

import { useParams } from "react-router-dom";

import useDataApi from "./Fetch";
import Toolbar, { useDropdown, useDevice, useTimestamp } from "./Toolbar";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";

function table(devices, sensor, sample_rate, start_date, end_date) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Time series</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {devices.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
                        <td>
                            <Plot src={sensorUrl(device, sensor, sample_rate, start_date, end_date)} />
                        </td>
                        <td>
                            <Button>Download</Button>
                        </td>
                    </tr>
                ))}
            </tbody>
        </Table>
    );
}

function sensorUrl(device, sensor, sample_rate, start_date, end_date) {
    const baseUrl = "/backend/plot_sensor";

    return `${baseUrl}/${device}/${sensor}/${sample_rate}/${start_date}/${end_date}`;
}

function useSensorToolbar(_device, _sensor, _sample_rate, _start_date, _end_date) {
    if (!_device) {
        _device = "PTL_RD_AT_001";
    }
    if (!_sensor) {
        _sensor = "temperature";
    }
    if (!_sample_rate) {
        _sample_rate = "AUTO";
    }
    if (!_start_date) {
        _start_date = "2020-05-07";
    }
    if (!_end_date) {
        _end_date = "2020-05-08";
    }

    const [device, setDevice] = useDevice(_device, true);
    const [sensor, setSensor] = useDropdown(_sensor, {
        values: ["ALL", "temperature", "humidity", "pressure", "brightness", "gas", "presence"],
        label: "Sensor",
    });
    const [sample_rate, setSampleRate] = useDropdown(_sample_rate, {
        values: ["AUTO", "1s", "10s"],
        label: "Sample rate",
    });
    const [start_date, setStartDate] = useTimestamp(_start_date);
    const [end_date, setEndDate] = useTimestamp(_end_date);

    const sensorToolbar = (
        <>
            {setDevice}
            {setStartDate}
            {setEndDate}
            {setSensor}
            {setSampleRate}
        </>
    );

    return [{ device, sensor, sample_rate, start_date, end_date }, sensorToolbar];
}

function AnalyticsSensor() {
    let params = useParams();

    const [{ device, sensor, sample_rate, start_date, end_date }, tools] = useSensorToolbar(
        params.device,
        params.sensor,
        params.sample_rate,
        params.start_date,
        params.end_date
    );

    const [url, setUrl] = useState(sensorUrl(device, sensor, sample_rate, start_date, end_date));

    useEffect(() => {
        const newUrl = sensorUrl(device, sensor, sample_rate, start_date, end_date);
        setUrl(newUrl);
        //props.history.push(newUrl);
    }, [device, sensor, sample_rate, start_date, end_date]);

    return (
        <>
            <Toolbar>{tools}</Toolbar>
            <span>{url}</span>
            {table([device], sensor, sample_rate, start_date, end_date)}
        </>
    );
}

export default AnalyticsSensor;
