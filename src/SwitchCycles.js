import React from "react";

import Button from "react-bootstrap/Button";

import { PlotData, PlotNew, usePlot, plotUrl } from "./BokehPlot";

import DeviceTable from "./DeviceTable";
import { LoadingAnimation } from "./Toolbar";

import { downloadFile, usePostApi } from "./Fetch";

const TableHeader = () => (
    <>
        <th>Cycles</th>
        <th>Download</th>
    </>
);

const TableRow = (props) => {
    const url = plotUrl('PlotOnOffCycles');
    const [{ data, isLoading, isError, errorMsg }, doFetch] = usePostApi(url, {device: props.device_id});

    return (
        <>
            <td>
                <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}><PlotData data={data}/></LoadingAnimation>
                {/* <PlotNew plot_name='PlotOnOffCycles' plot_parameters={{device: props.device_id}} /> */}
            </td>
            <td>
                <Button onClick={() => downloadFile('PlotOnOffCycles', {device: props.device_id}, `analytics_scenes_${props.device_id}.xlsx`)}>Download</Button>
            </td>
        </>
    );
}

const SwitchCycles = () => <DeviceTable format_header={TableHeader} format_row={TableRow} />;


export default SwitchCycles;
