import React from "react";

import { useParams } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Col from 'react-bootstrap/Col';

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

import useDateRange, { formatDate, parseDate } from "./DatePicker";

import { useDropdown, useTimestamp } from "./Toolbar";

function sensorUrl(device, sensor, sample_rate, start_date, end_date) {
    const baseUrl = "/backend/plot_sensor";
    return `${baseUrl}/${device}/${sensor}/${sample_rate}/${start_date}/${end_date}`;
}

function useSensorToolbar(_sensor, _sample_rate, _start_date, _end_date) {
    if (!_sensor) {
        _sensor = "temperature";
    }
    if (!_sample_rate) {
        _sample_rate = "AUTO";
    }
    if (!_start_date) {
        _start_date = "2020-04-04"; // TODO: set current date
    }
    if (!_end_date) {
        _end_date = "2020-04-05"; // TODO: set current date
    }

    const [sensor, setSensor] = useDropdown(_sensor, {
        values: ["ALL", "temperature", "humidity", "pressure", "brightness", "gas", "presence"],
        label: "Sensor",
    });
    const [sample_rate, setSampleRate] = useDropdown(_sample_rate, {
        values: ["AUTO", "1s", "10s"],
        label: "Sample rate",
    });

    
    //const [start_date, setStartDate] = useTimestamp(_start_date);
    //const [end_date, setEndDate] = useTimestamp(_end_date);

    const [start_date, end_date, setDateRange] = useDateRange(parseDate(_start_date).toDate(), parseDate(_end_date).toDate());

    const sensorToolbar = (
        <>
            <Col lg={4}>{setDateRange}</Col>
            <Col lg={2}>{setSensor}</Col>
            <Col lg={2}>{setSampleRate}</Col>
        </>
    );

    const plotUrl = (device) => sensorUrl(device, sensor, sample_rate, formatDate(start_date), formatDate(end_date));

    const tableRow = (props) => (
        <>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button>Download</Button>
            </td>
        </>
    );

    return [tableRow, sensorToolbar];
}

const TableHeader = () => (
    <>
        <th>Time series</th>
        <th>Download</th>
    </>
);

function AnalyticsSensor() {
    const { sensor, sample_rate, start_date, end_date } = useParams();
    const [tableRow, tools] = useSensorToolbar(sensor, sample_rate, start_date, end_date);

    return (
        <>
            <p>
                <b>Note:</b> If Sensor data is not cached, downloading of sensor data can take up to 1 minutes per day
                and device.
            </p>
            <DeviceTable format_header={TableHeader} format_row={tableRow} toolbar={tools} />
        </>
    );
}

export default AnalyticsSensor;
