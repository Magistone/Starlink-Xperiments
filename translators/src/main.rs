use std::{
    fs::File,
    io::{BufRead, BufReader},
    path::Path,
};

use csv::Writer;

const SUPPORTED_TYPES: [&str; 6] = [
    "device",
    "ip",
    "ping",
    "space_weather",
    "traceroute",
    "weather",
];

fn main() {
    if let Err(e) = run() {
        println!("{}", e); // "There is an error: Oops"
    }
}

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let input_file = std::env::args().nth(1).expect("No input file given.");
    let input_file = Path::new(&input_file);
    let output_file = input_file.with_extension("csv");

    let file_type = std::env::args()
        .nth(2)
        .unwrap_or_else(|| panic!("No file_type given. Supported types are: {SUPPORTED_TYPES:?}"));

    let input_file = File::open(input_file)?;
    let reader = BufReader::new(input_file);
    let writer = Writer::from_path(output_file)?;

    /* Choose which parser to invoke */
    match file_type.as_str() {
        "device" => export_csv_device(reader, writer)?,
        "ip" => export_csv_ip(reader, writer)?,
        "ping" => export_csv_ping(reader, writer)?,
        "space_weather" => export_csv_space_weather(reader, writer)?,
        "traceroute" => export_csv_traceroute(reader, writer)?,
        "weather" => export_csv_weather(reader, writer)?,
        _ => panic!("Unknown file type {file_type}. Supported types are: {SUPPORTED_TYPES:?}"),
    }

    Ok(())
}

fn export_csv_device(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",

        /*   ALIGNMENT (7)  */
        "alignment_tilt_angle_deg",
        "alignment_azimuth_deg",
        "alignment_elevation_deg",
        "alignment_desired_azimuth_deg",
        "alignment_desired_elevation_deg",
        "alignment_attitude_uncertainty_deg",
        "alignment_estimation_state",
        /*    NETWORK  (8)  */
        "network_is_cell_disabled",
        "network_snr_persistently_low",
        "network_snr_above_noise_floor",
        "network_pop_ping_ms",
        "network_pop_ping_droprate_%",
        "network_seconds_to_non_empty_slot",
        "network_throughput_down_bps",
        "network_throughput_up_bps",
        /*    ALERTS   (17)  */
        "alert_motors_stuck",
        "alert_thermal_throttle",
        "alert_thermal_shutdown",
        "alert_mast_not_near_vertical",
        "alert_unexpected_location",
        "alert_slow_ethernet_speeds",
        "alert_slow_ethernet_speeds_100",
        "alert_roaming",
        "alert_install_pending",
        "alert_is_heating",
        "alert_power_supply_thermal_throttle",
        "alert_is_power_save_idle",
        "alert_moving_while_not_mobile",
        "alert_moving_too_fast_for_policy",
        "alert_dbf_telem_stale",
        "alert_low_motor_current",
        "alert_lower_signal_than_predicted",
        /*    OUTAGE   (4)  */
        "outage_cause",
        "outage_start_ns",
        "outage_duration_ns",
        "outage_switched",
        /*     INFO    (7)  */
        "info_software_version",
        "info_country",
        "info_software_update_state",
        "info_software_update_progress",
        "info_disablement_code",
        "info_service_class",
        "info_mobility_class"
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record(
            [
                &record["timestamp"]["$date"].as_str().unwrap(),
                //&record["metadata"]["job_name"],
                &record["metadata"]["machine"].as_str().unwrap(),
                //&record["metadata"]["measurement"],

                /*   ALIGNMENT (7)   */
                &record["alignment"]["tilt_angle_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["azimuth_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["elevation_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["desired"]["azimuth_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["desired"]["elevation_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["attitude_uncertainty_deg"].as_f64().unwrap().to_string().as_str(),
                &record["alignment"]["estimation_state"].as_str().unwrap(),


                /*    NETWORK  (8)   */
                &i64::from(record["network"]["cell_disabled"].as_bool().unwrap()).to_string().as_str(),
                &i64::from(record["network"]["snr_persistently_low"].as_bool().unwrap()).to_string().as_str(),
                &i64::from(record["network"]["snr_above_noise_floor"].as_bool().unwrap()).to_string().as_str(),
                &record["network"]["pop_ping_ms"].as_f64().unwrap().to_string().as_str(),
                &record["network"]["pop_ping_drop_rate_percent"].as_f64().unwrap().to_string().as_str(),
                &record["network"]["seconds_to_non_empty_slot"].as_i64().unwrap().to_string().as_str(),
                &record["network"]["throughput"]["down_bps"].as_f64().unwrap().to_string().as_str(),
                &record["network"]["throughput"]["up_bps"].as_f64().unwrap().to_string().as_str(),


                /*    ALERTS   (17)  */
                "",
                &i64::from(record["alerts"]["thermal_throttle"].as_bool().unwrap_or(false)).to_string().as_str(),
                &i64::from(record["alerts"]["thermal_shutdown"].as_bool().unwrap_or(false)).to_string().as_str(),
                "",
                "",
                "",
                "",
                "",
                &i64::from(record["alerts"]["install_pending"].as_bool().unwrap_or(false)).to_string().as_str(),
                &i64::from(record["alerts"]["is_heating"].as_bool().unwrap_or(false)).to_string().as_str(),
                &i64::from(record["alerts"]["power_supply_thermal_throttle"].as_bool().unwrap_or(false)).to_string().as_str(),
                &i64::from(record["alerts"]["is_power_save_idle"].as_bool().unwrap_or(false)).to_string().as_str(),
                "",
                "",
                &i64::from(record["alerts"]["dbf_telem_stale"].as_bool().unwrap_or(false)).to_string().as_str(),
                "",
                &i64::from(record["alerts"]["lower_signal_than_predicted"].as_bool().unwrap_or(false)).to_string().as_str(),


                /*    OUTAGE   (4)   */
                &record["outage"]["cause"].as_str().unwrap_or(""),
                &record["outage"]["start_ns"].as_i64().unwrap_or(0).to_string().as_str(),
                &record["outage"]["duration_ns"].as_i64().unwrap_or(0).to_string().as_str(),
                &i64::from(record["outage"]["switched"].as_bool().unwrap_or(false)).to_string().as_str(),


                /*     INFO    (7)   */
                "",
                "",
                &record["info"]["software"]["update_state"].as_str().unwrap_or(""),
                &record["info"]["software"]["update_progress"].as_f64().unwrap_or(0.0).to_string().as_str(),
                "",
                "",
                ""
            ])?;
    }

    writer.flush()?;
    Ok(())
}

fn export_csv_ip(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",
        "v6",
        "v4",
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record(
            [
                &record["timestamp"]["$date"],
                //&record["metadata"]["job_name"],
                &record["metadata"]["machine"],
                //&record["metadata"]["measurement"],
                &record["v6"],
                &record["v4"],
            ]
            .map(|x| x.as_str().unwrap()),
        )?;
    }

    writer.flush()?;
    Ok(())
}

fn export_csv_ping(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",
        "metadata_target",
        "rtt_ms",
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record([
            &record["timestamp"]["$date"].as_str().unwrap(),
            //&record["metadata"]["job_name"].as_str().unwrap(),
            &record["metadata"]["machine"].as_str().unwrap(),
            //&record["metadata"]["measurement"].as_str().unwrap(),
            &record["metadata"]["target"].as_str().unwrap(),
            &record["rtt_ms"].as_f64().unwrap().to_string().as_str(),
        ])?;
    }

    writer.flush()?;
    Ok(())
}

fn export_csv_space_weather(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",
        "R",
        "S",
        "G",
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record(
            [
                &record["timestamp"]["$date"],
                //&record["metadata"]["job_name"],
                &record["metadata"]["machine"],
                //&record["metadata"]["measurement"],
                &record["R"],
                &record["S"],
                &record["G"],
            ]
            .map(|x| x.as_str().unwrap()),
        )?;
    }

    writer.flush()?;
    Ok(())
}

fn export_csv_traceroute(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",
        "target",
        "1_address",
        "1_rtt_ms",
        
        "2_address",
        "2_rtt_ms",
        
        "3_address",
        "3_rtt_ms",
        
        "4_address",
        "4_rtt_ms",
        
        "5_address",
        "5_rtt_ms",
        
        "6_address",
        "6_rtt_ms",
        
        "7_address",
        "7_rtt_ms",
        
        "8_address",
        "8_rtt_ms",
        
        "9_address",
        "9_rtt_ms",
        
        "10_address",
        "10_rtt_ms",
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record(
            [
                (record["timestamp"]["$date"].as_str().unwrap()),
                //&record["metadata"]["job_name"],
                (record["metadata"]["machine"].as_str().unwrap()),
                //&record["metadata"]["measurement"],
                (record["metadata"]["target"].as_str().unwrap()),

                (record["1"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["1"]["rtt_ms"].as_f64()).as_str(),

                (record["2"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["2"]["rtt_ms"].as_f64()).as_str(),

                (record["3"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["3"]["rtt_ms"].as_f64()).as_str(),

                (record["4"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["4"]["rtt_ms"].as_f64()).as_str(),
                
                (record["5"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["5"]["rtt_ms"].as_f64()).as_str(),

                (record["6"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["6"]["rtt_ms"].as_f64()).as_str(),
                
                (record["7"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["7"]["rtt_ms"].as_f64()).as_str(),

                (record["8"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["8"]["rtt_ms"].as_f64()).as_str(),

                (record["9"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["9"]["rtt_ms"].as_f64()).as_str(),

                (record["10"]["address"].as_str().unwrap_or("")),
                unwrap_f64(&record["10"]["rtt_ms"].as_f64()).as_str(),
            ])?;
    }

    fn unwrap_f64(opt: &Option<f64>) -> String {
        let value = opt.unwrap_or_else(|| 0.0);
        if value == 0.0 {
            return "".to_string();
        }
        value.to_string()
    }

    writer.flush()?;
    Ok(())
}

fn export_csv_weather(
    reader: BufReader<File>,
    mut writer: Writer<File>,
) -> Result<(), Box<dyn std::error::Error>> {
    writer.write_record([
        "timestamp",
        //"metadata_job_name",
        "metadata_machine",
        //"metadata_measurement",
        "temp_C",
        "cloud_area_fraction_%",
        "precipitation_amount_mm",
    ])?;

    for line in reader.lines() {
        let line: String = line?;
        let record: serde_json::Value = serde_json::from_str(line.as_str())?;

        writer.write_record(
            [
                &record["timestamp"]["$date"].as_str().unwrap(),
                //&record["metadata"]["job_name"],
                &record["metadata"]["machine"].as_str().unwrap(),
                //&record["metadata"]["measurement"],
                &record["temperature_celsius"].as_f64().unwrap().to_string().as_str(),
                &record["cloud_area_fraction_%"].as_f64().unwrap().to_string().as_str(),
                &record["precipitation_amount_mm"].as_f64().unwrap().to_string().as_str(),
            ])?;
    }

    writer.flush()?;
    Ok(())
}
