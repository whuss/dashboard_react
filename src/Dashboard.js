import React, { useState } from "react";

import Grid from "@material-ui/core/Grid";
import Paper from "@material-ui/core/Paper";
import Container from "@material-ui/core/Container";
import ScopedCssBaseline from "@material-ui/core/ScopedCssBaseline";
import Box from "@material-ui/core/Box";
import { Theme, createStyles, makeStyles, rgbToHex } from "@material-ui/core/styles";
import GazeChart from "./DashboardGazeChart";
import LightingModeChart from "./DashboardLightingModeChart";
import UsageChart from "./DashboardUsageChart";
import Doughnut from "./DashboardDoughnut";
import LightShowerChart from "./DashboardLightShowerChart";

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

const text =
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

const textShort =
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.";

const automaticColor = "red";
const monitorColor = "#008ef5";
const monitorColorRgb = [0, 142, 245];
const paperColor = "#00b100";
const paperColorRgb = [0, 177, 0];
const usageProfileColor = "#df892b";
const usageProfileColorRgb = [223, 137, 43];

const DashboardPanel = ({ title, children }) => {
    const classes = useStyles();

    return (
        <div style={{ position: "relative" }}>
            <div
                style={{
                    margin: 20,
                    paddingTop: 30,
                    paddingBottom: 30,
                    //  width: "500px",
                    //  height: "300px",
                    borderWidth: 1,
                    borderStyle: "dashed",
                    textAlign: "justify",
                }}
            >
                <ScopedCssBaseline>
                    <Container className={classes.root}>{children}</Container>
                </ScopedCssBaseline>
            </div>
            <div
                style={{
                    position: "absolute",
                    margin: 0,
                    top: 0,
                    left: 50,
                    padding: 9,
                    backgroundColor: "white",
                    fontWeight: "bolder",
                }}
            >
                {title}
            </div>
        </div>
    );
};

const useStyles = makeStyles((theme) =>
    createStyles({
        root: {
            background: "white",
        },
        dataBig: {
            fontSize: "20pt",
        },
        dataSmall: {
            fontSize: "16pt",
        },
        marginBottom: {
            marginBottom: 10,
        },
        marginTop: {
            marginTop: 10,
        },
        intensityGrid: {
            "& ul": {
                listStyleType: "none",
                margin: 0,
                padding: 0,
                "& li": {
                    float: "left",
                    width: "8.3333%",
                    height: 15,
                    textAlign: "center",
                    color: "#ecf0f1",
                    borderStyle: "solid",
                    borderColor: "white",
                    borderWidth: "1px",
                },
            },
        },
        histogramGrid: {
            "& ul": {
                listStyleType: "none",
                margin: 0,
                padding: 0,
                "& li": {
                    float: "left",
                    width: "10%",
                    height: 15,
                    textAlign: "center",
                    borderStyle: "solid",
                    borderColor: "white",
                    borderWidth: "1px",
                },
            },
        },
    })
);

const IntensityGrid = ({ intensities, colorRgb }) => {
    const classes = useStyles();

    const color = (intensity) => {
        const [r, g, b] = colorRgb;
        return `rgba(${r}, ${g}, ${b}, ${intensity / 100})`;
    };

    return (
        <Box className={classes.intensityGrid}>
            <ul>
                {intensities.map((intensity, i) => (
                    <li key={i} style={{ backgroundColor: color(intensity) }}>
                        &nbsp;
                    </li>
                ))}
            </ul>
        </Box>
    );
};

const HistogramGrid = ({ data, colorRgb }) => {
    const classes = useStyles();

    const color = (h) => {
        const [r, g, b] = colorRgb;
        return `rgba(${r}, ${g}, ${b}, ${h / 100})`;
    };

    return (
        <Box className={classes.histogramGrid}>
            <ul>
                {data.map((h, i) => (
                    <li key={i} style={{ backgroundColor: color(h) }}>
                        &nbsp;
                    </li>
                ))}
            </ul>
        </Box>
    );
};

const MonthView = () => {
    return (
        <Box className={"calendar"}>
            <ul>
                <li className="days">Mo</li>
                <li className="days">Tu</li>
                <li className="days">We</li>
                <li className="days">Th</li>
                <li className="days">Fr</li>
                <li className="days">Sa</li>
                <li className="days">Su</li>
                <li className="empty"></li>
                <li>1</li>
                <li>2</li>
                <li>3</li>
                <li>4</li>
                <li>5</li>
                <li>6</li>
                <li>7</li>
                <li>8</li>
                <li>9</li>
                <li className="selected">10</li>
                <li className="selected">11</li>
                <li>12</li>
                <li>13</li>
                <li>14</li>
                <li>15</li>
                <li className="selected">16</li>
                <li className="selected">17</li>
                <li>18</li>
                <li>19</li>
                <li>20</li>
                <li>21</li>
                <li>22</li>
                <li>23</li>
                <li>24</li>
                <li>25</li>
                <li>26</li>
                <li>27</li>
                <li>28</li>
                <li>29</li>
                <li>30</li>
                <li>31</li>
                <li className="empty">&nbsp;</li>
                <li className="empty">&nbsp;</li>
                <li className="empty">&nbsp;</li>
            </ul>
            June 2020
        </Box>
    );
};

const GeneralInformation = () => {
    const classes = useStyles();
    return (
        <DashboardPanel title="General Information">
            <Grid container direction="row" spacing={2}>
                <Grid item xs={12}>
                    <Box className={classes.dataBig}>PTL 001, Spain</Box>
                </Grid>
                <Grid item xs={6}>
                    <MonthView />
                </Grid>
                <Grid item xs={6}>
                    <MonthView />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const monitorTaskData = {
    changed: 12,
    duration: 1023,
    colorTemperatureLeft: 4000,
    colorTemperatureRight: 3700,
    intensityLeft: 67.5,
    intensityRight: 42.3,
    intensities: [100, 23, 43, 54, 12, 23, 54, 34, 23, 100, 23, 43, 12, 23, 54, 100, 23, 43, 54, 34, 23, 98, 42, 73],
};

const paperTaskData = {
    changed: 9,
    duration: 543,
    colorTemperatureLeft: 5000,
    colorTemperatureRight: 5300,
    intensityLeft: 42.0,
    intensityRight: 89.9,
    intensities: [50, 77, 32, 10, 12, 23, 43, 77, 33, 59, 43, 30, 43, 54, 98, 42, 73, 12, 23, 54, 34, 23, 100, 23],
};

const UsageProfile = () => {
    const classes = useStyles();

    const histogramData = [
        [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        [50, 20, 30, 40, 50, 60, 80, 70, 90, 40],
        [80, 20, 30, 70, 80, 90, 40, 50, 60, 40],
        [30, 20, 50, 60, 30, 40, 70, 80, 90, 15],
        [60, 20, 50, 40, 20, 26, 70, 11, 12, 12],
    ];

    const percentageData = [89, 56, 72, 43, 53];

    const ULine = ({ name, data, percentage }) => (
        <>
            <Grid container alignItems="center">
                <Grid xs={3} className={classes.marginBottom}>
                    <Box textAlign="left">{name}</Box>
                </Grid>
                <Grid xs={8} className={classes.marginBottom}>
                    <HistogramGrid data={data} colorRgb={usageProfileColorRgb} />
                </Grid>
                <Grid xs={1} className={classes.marginBottom}>
                    <Box style={{ marginLeft: 10 }} textAlign="right">
                        {percentage}%
                    </Box>
                </Grid>
            </Grid>
        </>
    );

    return (
        <DashboardPanel title="Usage profile">
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid container item xs={7} alignItems="center">
                    <ULine name="Mode usage" data={histogramData[0]} percentage={percentageData[0]} />
                    <ULine name="Interaction" data={histogramData[1]} percentage={percentageData[1]} />
                    <ULine name="Rebound" data={histogramData[2]} percentage={percentageData[2]} />
                    <ULine name="Frequency" data={histogramData[3]} percentage={percentageData[3]} />
                    <ULine name="Task" data={histogramData[4]} percentage={percentageData[4]} />

                    {/* <ULine name="Mode usage" data={data} percentage={89} />
                    <ULine name="Interaction" data={data} percentage={56} />
                    <ULine name="Rebound" data={data} percentage={72} />
                    <ULine name="Frequency" data={data} percentage={43} />
                    <ULine name="Task" data={data} percentage={53} /> */}
                </Grid>
                <Grid xs={5}>
                    <UsageChart color={usageProfileColor} data={percentageData} />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const TaskSettings = ({ title, data, color, colorRgb }) => {
    const classes = useStyles();

    const {
        changed,
        duration,
        colorTemperatureLeft,
        colorTemperatureRight,
        intensityLeft,
        intensityRight,
        intensities,
    } = data;

    const colorStyle = { color: color };

    return (
        <DashboardPanel title={`${title} task settings`}>
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="left">
                        <span className={classes.dataBig} style={colorStyle}>
                            {changed} times
                        </span>
                        <br />
                        changed
                    </Box>
                </Grid>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="right">
                        <span className={classes.dataBig} style={colorStyle}>
                            {duration} hrs
                        </span>
                        <br />
                        duration
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={colorStyle} textAlign="left">
                        {colorTemperatureLeft}K
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">Color temperature</Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={colorStyle} textAlign="right">
                        {colorTemperatureRight}K
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={colorStyle} textAlign="left">
                        {intensityLeft}%
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">Weighted intensity</Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={colorStyle} textAlign="right">
                        {intensityRight}%
                    </Box>
                </Grid>
                <Grid xs={12} className={classes.marginTop}>
                    <IntensityGrid intensities={intensities} colorRgb={colorRgb} />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const gazeDetectionData = {
    trackingTime: 435,
    derivedDetections: 93.5,
    totalMonitorDuration: 177,
    totalPaperDuration: 113,
    meanMonitorDuration: 112,
    meanPaperDuration: 89,
    dataMonitor: [0, 59, 12, 81, 56, 0],
    dataPaper: [0, 81, 56, 55, 95, 0],
};

const GazeDetection = ({ data }) => {
    const classes = useStyles();

    const {
        trackingTime,
        derivedDetections,
        totalMonitorDuration,
        totalPaperDuration,
        meanMonitorDuration,
        meanPaperDuration,
        dataMonitor,
        dataPaper,
    } = data;

    const monitorStyle = { color: monitorColor };
    const paperStyle = { color: paperColor };

    return (
        <DashboardPanel title="Gaze Detection">
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="left">
                        <span className={classes.dataBig}>{trackingTime} hrs</span>
                        <br />
                        tracking time
                    </Box>
                </Grid>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="right">
                        <span className={classes.dataBig}>{derivedDetections}%</span>
                        <br />
                        derived detections
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={monitorStyle} textAlign="left">
                        {totalMonitorDuration}&nbsp;hrs
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">Total task duration</Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={paperStyle} textAlign="right">
                        {totalPaperDuration}&nbsp;hrs
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={monitorStyle} textAlign="left">
                        {meanMonitorDuration}&nbsp;mins
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">Mean task duration</Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} style={paperStyle} textAlign="right">
                        {meanPaperDuration}&nbsp;mins
                    </Box>
                </Grid>
                <Grid xs={12} className={classes.marginTop}>
                    <GazeChart
                        monitorColor={monitorColor}
                        paperColor={paperColor}
                        dataMonitor={dataMonitor}
                        dataPaper={dataPaper}
                    />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const lightingModeData = {
    autoMode: 868,
    switchCycles: 27.3,
    autoOnly: 15,
    interactions: 178,
    modeChanges: 96,
    switchedOff: 68,
    dataAutomatic: [23, 12, 30, 66, 0, 0],
    dataMonitor: [0, 59, 12, 81, 56, 0],
    dataPaper: [0, 81, 56, 55, 95, 0],
};

const LightingMode = ({ data }) => {
    const classes = useStyles();

    const {
        autoMode,
        switchCycles,
        autoOnly,
        interactions,
        modeChanges,
        switchedOff,
        dataAutomatic,
        dataMonitor,
        dataPaper,
    } = data;

    return (
        <DashboardPanel title="Lighting mode usage">
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="left">
                        <span className={classes.dataBig}>{autoMode} hrs</span>
                        <br />
                        auto mode
                    </Box>
                </Grid>
                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="center">
                        <span className={classes.dataBig}>{switchCycles} daily</span>
                        <br />
                        switch cycles
                    </Box>
                </Grid>
                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="right">
                        <span className={classes.dataBig}>{autoOnly} days</span>
                        <br />
                        auto only
                    </Box>
                </Grid>

                <Grid xs={6}>
                    <Doughnut
                        firstLine={<span className={classes.dataBig}>89%</span>}
                        secondLine={
                            <span>
                                automatic
                                <br />
                                usage
                            </span>
                        }
                    />
                </Grid>

                <Grid xs={6}>
                    <Doughnut
                        firstLine={<span className={classes.dataBig}>80%</span>}
                        secondLine={
                            <span>
                                manual&nbsp;task
                                <br />
                                switch-offs
                            </span>
                        }
                    />
                </Grid>

                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="left">
                        interacted
                        <br />
                        <span className={classes.dataBig}>{interactions} times</span>
                    </Box>
                </Grid>
                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="center">
                        changed mode
                        <br />
                        <span className={classes.dataBig}>{modeChanges} times</span>
                    </Box>
                </Grid>
                <Grid xs={4} className={classes.marginBottom}>
                    <Box textAlign="right">
                        switched off
                        <br />
                        <span className={classes.dataBig}>{switchedOff} times</span>
                    </Box>
                </Grid>

                <Grid xs={12} className={classes.marginTop}>
                    <LightingModeChart
                        automaticColor={automaticColor}
                        monitorColor={monitorColor}
                        paperColor={paperColor}
                        dataAutomatic={dataAutomatic}
                        dataMonitor={dataMonitor}
                        dataPaper={dataPaper}
                    />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const lightShowerData = {
    notifications: 29,
    triggered: 17,
    duration: 178,
    daytimeRatio: 0.875,
    dataHistogram: [23, 12, 30, 66, 23, 40],
};

const LightShowerUsage = ({ data }) => {
    const classes = useStyles();

    const { notifications, triggered, duration, daytimeRatio, dataHistogram } = data;

    return (
        <DashboardPanel title="Light shower usage">
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="left">
                        <span className={classes.dataBig}>{notifications} times</span>
                        <br />
                        notified
                    </Box>
                </Grid>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="right">
                        <span className={classes.dataBig}>{triggered} times</span>
                        <br />
                        triggered
                    </Box>
                </Grid>

                <Grid xs={12}>
                    <Doughnut
                        firstLine={<span className={classes.dataBig}>72%</span>}
                        secondLine={
                            <span>
                                notification
                                <br />
                                rebound
                            </span>
                        }
                    />
                </Grid>

                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="left">
                        duration
                        <br />
                        <span className={classes.dataBig}>{duration} mins</span>
                    </Box>
                </Grid>
                <Grid xs={6} className={classes.marginBottom}>
                    <Box textAlign="right">
                        daytime ratio
                        <br />
                        <span className={classes.dataBig}>{daytimeRatio}</span>
                    </Box>
                </Grid>

                <Grid xs={12} className={classes.marginTop}>
                    <LightShowerChart
                        automaticColor={automaticColor}
                        monitorColor={monitorColor}
                        paperColor={paperColor}
                        data={dataHistogram}
                    />
                </Grid>
            </Grid>
        </DashboardPanel>
    );
};

const Dashboard = () => {
    return (
        <Grid container>
            <Grid xs={3}>
                <Grid container direction="column">
                    <GeneralInformation />
                    <TaskSettings
                        title="Monitor"
                        data={monitorTaskData}
                        color={monitorColor}
                        colorRgb={monitorColorRgb}
                    />
                    <TaskSettings title="Paper" data={paperTaskData} color={paperColor} colorRgb={paperColorRgb} />
                </Grid>
            </Grid>
            <Grid xs={6}>
                <Grid container direction="column">
                    <LightingMode data={lightingModeData} />
                    <UsageProfile />
                </Grid>
            </Grid>
            <Grid xs={3}>
                <Grid container direction="column">
                    <LightShowerUsage data={lightShowerData} />
                    <GazeDetection data={gazeDetectionData} />
                </Grid>
            </Grid>
            <Grid xs={12} justify="space-between">
                <Grid container direction="column">
                    <DashboardPanel title="Occupancy profile">{textShort}</DashboardPanel>
                </Grid>
            </Grid>
        </Grid>
    );
};

export default Dashboard;
