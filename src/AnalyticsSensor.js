import React from "react";

import { useParams } from "react-router-dom";

import Button from "react-bootstrap/Button";

import DeviceTable from "./DeviceTable";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";
import { downloadFile } from "./Fetch";

import useDateRange, { formatDate, parseDate, yesterday, dayBeforeYesterday } from "./DatePicker";

import { useDropdown } from "./Toolbar";

function useSensorToolbar(_sensor, _sample_rate, _start_date, _end_date) {
    if (!_sensor) {
        _sensor = "temperature";
    }
    if (!_sample_rate) {
        _sample_rate = "AUTO";
    }
    if (!_start_date) {
        _start_date = formatDate(dayBeforeYesterday());
    }
    if (!_end_date) {
        _end_date = formatDate(yesterday());
    }

    console.log(`start_date = ${_start_date}, end_date = ${_end_date}`);

    const [sensor, setSensor] = useDropdown(_sensor, {
        values: ["ALL", "temperature", "humidity", "pressure", "brightness", "gas", "presence"],
        label: "Sensor",
    });
    const [sample_rate, setSampleRate] = useDropdown(_sample_rate, {
        values: ["AUTO", "1s", "1Min", "10Min", "30Min", "1h", "2h", "6h", "12h", "1d", "7d"],
        label: "Sample rate",
    });

    const [start_date, end_date, setDateRange] = useDateRange(
        parseDate(_start_date).toDate(),
        parseDate(_end_date).toDate()
    );

    const params = `/analytics/sensor/${sensor}/${sample_rate}/${formatDate(start_date)}/${formatDate(end_date)}`;

    const sensorToolbar = (
        <>
            {setDateRange}
            {setSensor}
            {setSampleRate}
        </>
    );

    function plot_parameters(device) {
        return {
            device: device,
            start_date: formatDate(start_date),
            end_date: formatDate(end_date),
            sensors: sensor,
            sample_rate: sample_rate,
        };
    }

    return [sensorToolbar, plot_parameters, params];
}

function rowFactory(plot_parameters) {
    const TableRow = (props) => {
        const device = props.device_id;
        const plot_name = "PlotSensors";
        const file_name = `analytics_sensor_${device}.xlsx`;
        const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters(device), false);

        return (
            <>
                <td>
                    <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                        {plot}
                    </LoadingAnimation>
                </td>
                <td>
                    <Button onClick={() => downloadFile(plot_name, plot_parameters(device), file_name)}>
                        Download
                    </Button>
                </td>
            </>
        );
    };

    return TableRow;
}

const TableHeader = () => (
    <>
        <th>Time series</th>
        <th>Download</th>
    </>
);

const AnalyticsSensor = (props) => {
    const { sensor, sample_rate, start_date, end_date } = useParams();
    const [tools, plot_parameters, params] = useSensorToolbar(sensor, sample_rate, start_date, end_date);
    const TableRow = rowFactory(plot_parameters);

    return (
        <>
            <p>
                <b>Note:</b> If Sensor data is not cached, downloading of sensor data can take up to 1 minutes per day
                and device.
            </p>
            <DeviceTable
                format_header={TableHeader}
                format_row={TableRow}
                toolbar={tools}
                params={params}
                devices={props.devices}
            />
        </>
    );
};

export default AnalyticsSensor;
