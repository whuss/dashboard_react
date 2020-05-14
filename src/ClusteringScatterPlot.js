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

const columns = [];

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
            dimensions: plotDimensions,
        };
    }

    return [sensorToolbar, plot_parameters];
}

const ScatterPlot = (props) => {
    const plot_name = props.plot_name;
    const x_axis = props.x_axis;
    const y_axis = props.y_axis;
    var plot_parameters = props.plot_parameters;
    plot_parameters.x_axis = x_axis;
    plot_parameters.y_axis = y_axis;

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

        const rows = ["d_0", "d_1"];

        const fields = undefined;
        //const [{ fields, isLoading, isError, errorMsg }, plot] = usePlot(plot_name, plot_parameters(props.device_id), false);

        function drawRow(y_axis) {
            const rowElement = rows.map((x_axis) => (
                
                    <ScatterPlot
                        plot_name={plot_name}
                        plot_parameters={plot_parameters(device)}
                        x_axis={x_axis}
                        y_axis={y_axis}
                    />
            ));
            return (<Row>{rowElement}</Row>)
        }

        return (
            <>
                <td>{fields && fields.significant_dimensions}</td>
                <td>
                    <Container>{rows.map((y_axis) => drawRow(y_axis))}</Container>
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
        <th>PCA Dimensions</th>
        <th>Cluster scatter plot</th>
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
