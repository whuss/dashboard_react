import React from "react";

import Button from "react-bootstrap/Button";

import Plot from "./BokehPlot";
import DeviceTable from "./DeviceTable";

import { downloadFile } from "./Fetch";

function plotUrl(device) {
    return `/backend/plot_analytics_scenes/${device}`;
}

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    return (
        <>
            <td>
                <Plot src={plotUrl(props.device_id)} />
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotSceneDurations', {device: props.device_id}, `analytics_scenes_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
};


const AnalyticsScenes = () => (
    <>
        <p>
            <b>Note:</b> Data from days where the total time of all scenes is less than 30 minutes are excluded form the
            dataset.
        </p>
        <DeviceTable format_header={TableHeader} format_row={TableRow} />
    </>
);

export default AnalyticsScenes;
