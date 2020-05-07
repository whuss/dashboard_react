import React from "react";

import Table from "react-bootstrap/Table";
import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

function plotUrl(device) {
    return `/backend/plot_analytics_connection/${device}`;
}

function table(data) {
    return (
        <Table className={"dataTable"} hover>
            <thead>
                <tr>
                    <th>Device ID</th>
                    <th>Cycles</th>
                    <th>Download</th>
                </tr>
            </thead>
            <tbody>
                {data.map((device) => (
                    <tr key={device}>
                        <th>{device}</th>
                        <td>
                            <Plot src={plotUrl(device)} />
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

const AnalyticsConnection = () => (
    <>
        <p>A data loss is detected when no data is received from the device for at least two minutes.</p>
        <p>
            Data from a day is excluded from analysis when either the downtime percentage is bigger than 5%, or the
            number of datalosses, i.e. the number of time intervals where the device has been offline, exceeds 5.
        </p>
        <p>
            <b>Note:</b> There is no connection data available for dates before 12.03.2020, these dates are always
            considered to have 0% downtime.
        </p>
        <DeviceTable format_table={table} />
    </>
);

export default AnalyticsConnection;
