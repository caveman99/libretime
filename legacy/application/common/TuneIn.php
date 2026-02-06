<?php

class Application_Common_TuneIn
{
    /**
     * @param $title  url encoded string
     * @param $artist url encoded string
     * Update with all fields (duration enables auto-expiration for type=dynamic)
     * curl "http://localhost:9000/input/dynamic?input=radio-live&songID=123&artist=Artist&title=Song&duration=03:45&secret=supersecret123"
     */
    public static function sendMetadataToTunein($title, $artist, $file_id, $duration)
    {
        $credQryStr = self::getCredentialsQueryString();
        $metadataQryStr = '&title=' . $title . '&artist=' . $artist . '&duration=' . $duration . '&songID=' . $file_id;

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $credQryStr . $metadataQryStr);
        curl_setopt($ch, CURLOPT_FAILONERROR, 1);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);

        $xmlResponse = curl_exec($ch);
        if (curl_error($ch)) {
            Logging::error('Failed to reach Router: ' . curl_errno($ch) . ' - ' . curl_error($ch) . ' - ' . curl_getinfo($ch, CURLINFO_EFFECTIVE_URL));
        }
        curl_close($ch);

/*        $xmlObj = new SimpleXMLElement($xmlResponse);
        if (!$xmlObj || $xmlObj->head->status != '200') {
            Logging::info('Error occurred pushing metadata to Router:');
            Logging::info($xmlResponse);
        } elseif ($xmlObj->head->status == '200') {*/
            Application_Model_Preference::setLastTuneinMetadataUpdate(time());
//        }
    }

    private static function getCredentialsQueryString()
    {
        $tuneInStationID = Application_Model_Preference::getTuneinStationId();
        $tuneInPartnerID = Application_Model_Preference::getTuneinPartnerId();
        $tuneInPartnerKey = Application_Model_Preference::getTuneinPartnerKey();

        return $tuneInPartnerID . '?secret=' . $tuneInPartnerKey . '&input=' . $tuneInStationID;
    }
}
