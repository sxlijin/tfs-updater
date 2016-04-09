// Copyright (c) 2016 Aging Miser

// This file is part of TFS HISCORES UPDATER.
//
// TFS HISCORES UPDATER is free software: you can redistribute it and/or
// modify it under the terms of the GNU General Public License as published
// by the Free Software Foundation, either version 3 of the License, or (at
// your option) any later version.
//
// TFS HISCORES UPDATER is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
// Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with TFS HISCORES UPDATER. If not, see http://www.gnu.org/licenses/.



// array that represents what each line in the hiscores_lite CSV represents
var received_order = [ 'Total level',
       /* skills */    'Attack', 'Defence', 'Strength', 'Constitution',
                       'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting',
                       'Fletching', 'Fishing', 'Firemaking', 'Crafting',
                       'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving',
                       'Slayer', 'Farming', 'Runecrafting', 'Hunter',
                       'Construction', 'Summoning', 'Dungeoneering',
                       'Divination', 'Invention',
    /* minigames */    'Bounty Hunter', 'B.H. Rogues', 'Dominion Tower',
                       'The Crucible', 'Castle Wars games', 'B.A. Attackers',
                       'B.A. Defenders', 'B.A. Collectors', 'B.A. Healers',
                       'Duel Tournament', 'Mobilising Armies', 'Conquest',
                       'Fist of Guthix', 'GG: Athletics', 'GG: Resource Race',
                       'WE2: Armadyl lifetime contribution',
                       'WE2: Bandos lifetime contribution',
                       'WE2: Armadyl PvP kills', 'WE2: Bandos PvP kills',
                       'Robbers caught during Heist',
                       'loot stolen during Heist', 'CFP: 5 game average',
                       'AF15: Cow Tipping',
                       'AF15: Rats killed after the miniquest.'
                       ];

// array that represents the skills/minigames to filter for
var hiscores_order = [ 'Attack', 'Strength', 'Defence', 'Constitution', 'Ranged',
                       'Magic', 'Prayer', 'Runecrafting', 'Crafting', 'Mining',
                       'Smithing', 'Woodcutting', 'Firemaking', 'Fishing', 'Cooking',
                       'Dungeoneering', 'Fist of Guthix'
                       ];

/**
 * Retrieves the hiscores for a specified player using the RS API.
 * @param {string} rsn The username of the player to retrieve hiscores for.
 * @return {string} The API-generated CSV for that player's hiscores; null if 404.
 */
function getHiscoresFor(rsn) {
    if (rsn == undefined) return null;
    var url = 'http://hiscore.runescape.com/index_lite.ws?player=%s';
    url = Utilities.formatString(url, rsn);
    
    // error is raised on 404, must catch
    try {
        var response = UrlFetchApp.fetch(url);
        return response.getContentText();
    }
    catch (e) {
        Logger.log('ERROR while retrieving hiscores for %s: %s', rsn, e);
        return null;
    }
}


/**
 * Retrieves the current memberlist of TFS (sourcing data from db-memberlist).
 * @return {Array} List of strings, where each string is the RSN of someone in TFS.
 */
function getMemberlist() {
        //Google API magic.
    var hs_spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var hs_sheet_memberlist = hs_spreadsheet.getSheetByName('db-memberlist');
    var hs_values_memberlist = hs_sheet_memberlist.getRange('A:A').getValues();
    
    var memberlist = hs_values_memberlist.map(function(e) { return String(e[0]); });
    memberlist = memberlist.filter(function(e) { return e.length > 0; });
    
    return memberlist;
}


/**
 * Retrieves the hiscores for everyone in TFS.
 * @return {Object} Associative array with RSN's as keys and Array of F2P stats as values.
 */
function getHiscores() {
    var memberlist = getMemberlist();
    var hiscore_data = {};
    
    for (var i = 0; i < memberlist.length; i++) {
        var rsn = memberlist[i], data = getHiscoresFor(rsn);
        if (data == null) {
            Logger.log('WARNING: was unable to retrieve hiscores for %s', rsn);
        }
        else {
            var newline_delimited_data = data.trim().split('\n');
            if (newline_delimited_data.length != received_order.length) {
                Logger.log('FATAL ERROR: format of retrieved hiscore data unrecognized');
                Logger.log('             (Maybe a skill or minigame was added?)');
                Logger.log('             See data dump below.');
                for (var k = 0; k < newline_delimited_data.length; k++) {
                    Logger.log('%s %s %s', k, newline_delimited_data[k], received_order[k]);
                }
            }
            
            var parsed_data = {};
            for (var j = 0; j < newline_delimited_data.length; j++) {
                parsed_data[received_order[j]] = newline_delimited_data[j].split(',').slice(1);
            }
            
            var hiscoreList = hiscores_order.map(function(e) { return parsed_data[e]; })
                                            .reduce(function(prev, curr) { return prev.concat(curr); });
            hiscore_data[rsn] = [rsn].concat(hiscoreList);
            //Logger.log('%s', hiscore_data[rsn]);
        }
    }
    
    return hiscore_data;
}


/**
 * Automatically updates the hiscore data in db-main.
 * @return {null}
 */
function updateHiscores() {
    var hs_spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    var hs_sheet_main = hs_spreadsheet.getSheetByName('db-main');
    var hs_sheet_main_range = hs_sheet_main.getRange(1, 1, 
                                                     hs_sheet_main.getLastRow(), 
                                                     hs_sheet_main.getLastColumn());
    var updated_data = getHiscores();
    var updated_table = [];
    
    // convert the updated hiscore data to spreadsheet format
    for (var rsn in updated_data) {
        if (!updated_data.hasOwnProperty(rsn)) continue;
        var row_data = updated_data[rsn];
        row_data = [getUTCTimestamp()].concat(row_data[0], '', row_data.slice(1));
        updated_data[rsn] = row_data;
    }
    
    //for (var rsn in updated_data) { Logger.log(updated_data[rsn][1]); }
    //Logger.log('\n\n');
    
    // if people have been removed from the memberlist, preserve their hiscore data
    var old_hiscore_data = hs_sheet_main_range.getValues();
    for (var i in old_hiscore_data) {
        var row = old_hiscore_data[i]; rsn = row[1];
        if (updated_data[rsn] == undefined) { updated_data[rsn] = row; }
    }
    
    //for (var rsn in updated_data) { Logger.log(updated_data[rsn][1]); }
    //Logger.log('\n\n');
    
    // build the table to replace the current sheet with
    for (var rsn in updated_data) {
        if (updated_data.hasOwnProperty(rsn)) updated_table.push(updated_data[rsn]);
    }
    
    for (var i in updated_table) { Logger.log(updated_table[i][1]); }
    
    
    // wipe out outdated hiscores
    hs_sheet_main_range.clearContent();
    
    // replace with updated hiscores
    hs_sheet_main.getRange(1, 1, updated_table.length, updated_table[0].length).setValues(updated_table);
}    


/**
 * Generates a timestamp with the UTC time corresponding to when the method was called.
 * @return {string} YYYY-MM-DD-HH-MM-SS format string representing current UTC time
 */
function getUTCTimestamp() {
    var date = new Date();
    var str = Utilities.formatString('%04d-%02d-%02d-%02d-%02d-%02d',
                                     date.getUTCFullYear(),
                                     date.getUTCMonth() + 1,
                                     date.getUTCDate(),
                                     date.getUTCHours(),
                                     date.getUTCMinutes(),
                                     date.getUTCSeconds()
                                     );
    return str;
}
