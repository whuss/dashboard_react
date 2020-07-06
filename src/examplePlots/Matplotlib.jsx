import React, { useEffect } from "react";
import Button from "react-bootstrap/Button";

import { usePlot } from "../framework/Plot";
import { LoadingAnimation, useDropdown } from "../framework/Toolbar";
import { downloadFile } from "../framework/Fetch";

const Plot = () => {
    const [sigma, setSigma] = useDropdown(15, {
        values: [5, 15, 25],
        label: "sigma",
    });
    const [mu, setMu] = useDropdown(100, {
        values: [50, 100, 150],
        label: "mu",
    });
    const plot_name = "PlotExampleMatplotlib";
    const file_name = "example_data.xlsx";
    const { flags, plot, plotParameters, setPlotParameters } = usePlot(plot_name, { sigma: sigma, mu: mu });
    const { fields, isLoading, isError, errorMsg } = flags;

    useEffect(() => {
        setPlotParameters({ sigma: sigma, mu: mu });
    }, [sigma, mu]);

    return (
        <>
            {setSigma}
            {setMu}
            <LoadingAnimation isLoading={isLoading} isError={isError} errorMsg={errorMsg}>
                {plot}
            </LoadingAnimation>
            {!isLoading && !isError && (
                <Button onClick={() => downloadFile(plot_name, plotParameters, file_name)}>Download</Button>
            )}
        </>
    );
};

export default Plot;
