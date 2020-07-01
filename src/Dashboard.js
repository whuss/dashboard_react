import React, { useState } from "react";

import Grid from "@material-ui/core/Grid";
import Paper from '@material-ui/core/Paper';
import Container from '@material-ui/core/Container';
import ScopedCssBaseline from '@material-ui/core/ScopedCssBaseline';
import Box from '@material-ui/core/Box';
import { Theme, createStyles, makeStyles, rgbToHex } from '@material-ui/core/styles';

import useDataApi from "./Fetch";

import { LoadingAnimation } from "./Toolbar";

const text =
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";

const textShort =
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.";


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
                <Container className={classes.root}>
                    {children}
                </Container>
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
        fontSize: '20pt',
        color: '#008ef5',
    },
    dataSmall: {
        fontSize: '16pt',
        color: '#008ef5',
    },
    marginBottom: {
        marginBottom: 10,
    },
    marginTop: {
        marginTop: 10,
    },
    intensityGrid: {
        '& ul': {
            listStyleType: "none",
            margin: 0,
            padding: 0,
            '& li': {
                float: "left",
                width: "8.3333%",
                height: 15,
                textAlign: 'center',
                color: '#ecf0f1',
                borderStyle: 'solid',
                borderColor: 'white',
                borderWidth: '1px',
            }
        }
    }
  }),
);

const intensities = [100, 23, 43, 54, 12, 23, 54, 34, 23, 100, 23, 43,
                     12, 23, 54, 100, 23, 43, 54, 34, 23, 98, 42, 73];

const IntensityGrid = ({intensities}) => {
    const classes = useStyles();

    const color = (intensity) => {
        const r = 0;
        const g = 142;
        const b = 245;
        return `rgba(${r}, ${g}, ${b}, ${intensity / 100})`;
    }

    return (
        <Box className={classes.intensityGrid}>
            <ul>
                {intensities.map((intensity, i) => <li key={i} style={{backgroundColor: color(intensity)}}>&nbsp;</li>)}
            </ul>
        </Box>
    )
}

const MonthView = () => {
    return (
        <div className="calendar">
            <ul>
                <li>Mo</li>
                <li>Tu</li>
                <li>We</li>
                <li>Th</li>
                <li>Fr</li>
                <li>Sa</li>
                <li>Su</li>
                <li>&nbsp;</li>
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
                <li>&nbsp;</li>
                <li>&nbsp;</li>
                <li>&nbsp;</li>
            </ul>
            June 2020
        </div>
    );
};

const GeneralInformation = () => {
    return (
        <DashboardPanel title="General Information">
                    <Grid container direction="row" spacing={2}>
                        <Grid item xs={12}>
                            PTL 001, Spain
                        </Grid>
                        <Grid item xs={6}>
                            <MonthView/>
                        </Grid>
                        <Grid item xs={6}>
                            <MonthView/>
                            </Grid>
                    </Grid>
                    </DashboardPanel>
    );
}

const monitorTaskData = {
    changed: 12,
    duration: 1023,
    colorTemperatureLeft: 4000,
    colorTemperatureRight: 3700,
    intensityLeft: 67.5,
    intensityRight: 42.3,
    intensities: [100, 23, 43, 54, 12, 23, 54, 34, 23, 100, 23, 43,
                  12, 23, 54, 100, 23, 43, 54, 34, 23, 98, 42, 73]
}

const paperTaskData = {
    changed: 9,
    duration: 543,
    colorTemperatureLeft: 5000,
    colorTemperatureRight: 5300,
    intensityLeft: 42.0,
    intensityRight: 89.9,
    intensities: [50, 77, 32, 10, 12, 23, 43, 77, 33, 59, 43, 30,
                  43, 54, 98, 42, 73,12, 23, 54, 34, 23, 100, 23]
}


const TaskSettings = ({title, data}) => {
    const classes = useStyles();

    const {changed, duration, colorTemperatureLeft, colorTemperatureRight, intensityLeft, intensityRight, intensities} = data;

    return (
        <DashboardPanel title={`${title} task settings`}>
            <Grid container justify="space-between" alignItems="center" spacing={2}>
                <Grid xs={6} className={classes.marginBottom}>
                <Box textAlign="left">
                    <span className={classes.dataBig}>{changed} times</span><br/>
                    changed
                    </Box>
                </Grid>
                <Grid xs={6} className={classes.marginBottom}>
                <Box textAlign="right">
                    <span className={classes.dataBig}>{duration} hrs</span><br/>
                    duration
                </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} textAlign="left">
                        {colorTemperatureLeft}K
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">
                        Color temperature
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} textAlign="right">
                        {colorTemperatureRight}K    
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} textAlign="left">
                        {intensityLeft}%
                    </Box>
                </Grid>
                <Grid xs={6}>
                    <Box textAlign="center">
                        Weighted intensity
                    </Box>
                </Grid>
                <Grid xs={3}>
                    <Box className={classes.dataSmall} textAlign="right">
                        {intensityRight}%
                    </Box>
                </Grid>
                <Grid xs={12} className={classes.marginTop}>
                    <IntensityGrid intensities={intensities}/>
                </Grid>
            </Grid>
        </DashboardPanel>
    );
}

const Dashboard = () => {
    return (
        <Grid container>
            <Grid xs={3}>
                <Grid container direction="column">
                    <GeneralInformation />
                    <TaskSettings title="Monitor" data={monitorTaskData} />
                    <TaskSettings title="Paper" data={paperTaskData} />
                </Grid>
            </Grid>
            <Grid xs={6}>
                <Grid container direction="column">
                    <DashboardPanel title="Lighting mode usage">{text}</DashboardPanel>
                    <DashboardPanel title="Usage Profile">{text}</DashboardPanel>
                </Grid>
            </Grid>
            <Grid xs={3}>
                <Grid container direction="column">
                    <DashboardPanel title="Light shower usage">{textShort}</DashboardPanel>
                    <DashboardPanel title="Gaze detection">{textShort}</DashboardPanel>
                </Grid>
            </Grid>
            <Grid xs={12}>
                <Grid container direction="column">
                    <DashboardPanel title="Occupancy profile">{textShort}</DashboardPanel>
                </Grid>
            </Grid>
        </Grid>
        
    );
};

export default Dashboard;
