import logging
import os
import time

logger = logging.getLogger("PLEX")
logger.setLevel(logging.DEBUG)


def scan(config, lock, path, scan_for, section):
    scan_path = ""

    # sleep for delay
    logger.info("Scanning '%s' in %d seconds", path, config['SERVER_SCAN_DELAY'])
    if config['SERVER_SCAN_DELAY']:
        time.sleep(config['SERVER_SCAN_DELAY'])

    # check file exists
    if scan_for == 'radarr':
        checks = 0
        while True:
            checks += 1
            if os.path.exists(path):
                logger.info("File '%s' exists on check %d of %d, proceeding with scan", path, checks,
                             config['SERVER_MAX_FILE_CHECKS'])
                scan_path = os.path.dirname(path)
                break
            elif checks >= config['SERVER_MAX_FILE_CHECKS']:
                logger.info("File '%s' exhausted all available checks, aborting scan", path)
                return
            else:
                logger.info("File '%s' did not exist on check %d of %d, checking again in 60 seconds", path, checks,
                             config['SERVER_MAX_FILE_CHECKS'])
                time.sleep(60)

    else:
        # sonarr doesnt pass the sonarr_episodefile_path in webhook, so we cannot check until this is corrected.
        scan_path = path

    # build plex scanner command
    if os.name == 'nt':
        final_cmd = '""%s" --scan --refresh --section %s --directory "%s""' \
                    % (config['PLEX_SCANNER'], str(section), scan_path)
    else:
        cmd = 'export LD_LIBRARY_PATH=' + config['PLEX_LD_LIBRARY_PATH'] \
              + ';export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR=' \
              + config['PLEX_SUPPORT_DIR'] + ';' + config['PLEX_SCANNER'] + ' --scan --refresh --section ' \
              + str(section) + ' --directory \\"' + scan_path + '\\"'
        final_cmd = 'sudo -u %s bash -c "%s"' % (config['PLEX_USER'], cmd)

    # invoke plex scanner
    with lock:
        logger.debug("Using:\n%s", final_cmd)
        os.system(final_cmd)
        logger.info("Finished")
    return


def show_sections(config):
    if os.name == 'nt':
        final_cmd = '""%s" --list"' % config['PLEX_SCANNER']
    else:
        cmd = 'export LD_LIBRARY_PATH=' + config['PLEX_LD_LIBRARY_PATH'] \
              + ';export PLEX_MEDIA_SERVER_APPLICATION_SUPPORT_DIR=' \
              + config['PLEX_SUPPORT_DIR'] + ';' + config['PLEX_SCANNER'] + ' --list'
        final_cmd = 'sudo -u %s bash -c "%s"' % (config['PLEX_USER'], cmd)
    os.system(final_cmd)