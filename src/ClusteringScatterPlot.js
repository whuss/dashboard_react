import React from "react";

import { useParams } from "react-router-dom";

import Button from "react-bootstrap/Button";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import Container from "react-bootstrap/Container";

import DeviceTable from "./DeviceTable";

import Plot from "./BokehPlot";

import { usePlot } from "./BokehPlot";
import { LoadingAnimation } from "./Toolbar";
import { downloadFile } from "./Fetch";

import { useDropdown } from "./Toolbar";

import Spinner from "react-bootstrap/Spinner";

const columns = [
];

const bigSpinnerStyle = {
    width: "300px",
    height: "300px",
    verticalAlign: "middle",
    display: "table-cell",
    textAlign: "center",
};

const BigSpinner = (props) => (
    <div style={bigSpinnerStyle}>
        <Spinner animation="border" size="sm" variant="secondary" />
    </div>
);

function useClusteringToolbar(_dimension) {
    if (!_dimension) {
        _dimension = 4;
    }

    const [plotDimensions, setPlotDimensions] = useDropdown(_dimension, {
        values: [2, 3, 4, 5, 6],
        label: "Dimensions",
    });

    //const params = `/clustring/input_distributation/${transformation}`;

    const sensorToolbar = <>{setPlotDimensions}</>;

    function plot_parameters(device) {
        return {
            device: device,
            sample_size: 5000,
            dimensions: plotDimensions
        };
    }

    return [sensorToolbar, plot_parameters];
}

const DistributionPlot = (props) => {
    const plot_name = props.plot_name;
    var plot_parameters = props.plot_parameters;
    plot_parameters.column = props.column;

    const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters, false);

    return (
        <>
            <Col>
                <LoadingAnimation style={bigSpinnerStyle} isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                    {plot}
                </LoadingAnimation>
            </Col>
        </>
    );
};

function rowFactory(plot_parameters) {
    const TableRow = (props) => {
        const device = props.device_id;
        const plot_name = "PlotClusteringScatterPlot";
        const file_name = `clustering_scatter_plot_${props.device_id}.xlsx`;

        return (
            <>
                <td>
                    <DistributionPlot plot_name={plot_name} plot_parameters={plot_parameters(device)} />
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
        <th>Input Data</th>
        <th>Download</th>
    </>
);

const ClusteringScatterPlot = (props) => {
    const { dimension } = useParams();
    const [tools, plot_parameters] = useClusteringToolbar(dimension);
    const TableRow = rowFactory(plot_parameters);

    return (
        <>
            <p>
                <b>Warning:</b> Plotting of the distributions can take a very long time.
            </p>
            <DeviceTable format_header={TableHeader} format_row={TableRow} toolbar={tools} devices={props.devices} />
        </>
    );
};

export default ClusteringScatterPlot;
