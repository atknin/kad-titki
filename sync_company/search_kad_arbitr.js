(function(){
    

    $('#sug-dates .from input').val('[date_from]');
    $('#sug-dates .from input').attr('class','');

    $('#sug-participants .tag textarea').text('[inn_ogrn]');
    $('#sug-participants .tag textarea').attr('class','');

    $('#b-form-submit button').click();
    $('#b-form-submit button').click();
    if($('html:contains("Ошибка 429")').length > 0)  {back_to_python({'error': 'error 429'},{'cookie':'error'})};
    var getcookies = function(){
        var pairs = document.cookie.split(";");
        var cookies = {};
        for (var i=0; i<pairs.length; i++){
            var pair = pairs[i].split("=");
            cookies[(pair[0]+'').trim()] = unescape(pair.slice(1).join('='));
        }
        return cookies;
    }

    try { setTimeout(
            function() {
                if($('.b-results').attr('class').includes('g-hidden'))  {back_to_python({'error': 'Not Found'},getcookies())};
                if($('html:contains("Ошибка 429")').length > 0)  { back_to_python({'error': 'error 429'},getcookies()); };
                var my_cases = $('#b-cases tbody tr');
                var data = {'items':[],'pages':$('#documentsPagesCount').val(),'date_from':$('#sug-dates .from input').val()}
                
                for (var i = 0; i < my_cases.length; i++) {
                  var line = my_cases.eq(i).find('td');
                  var element = {}
                  element['uid'] = line.eq(0).find('a').attr('href').split('/').pop();
                  element['case'] = line.eq(0).find('a').text().replace(/\s\s+/g, ' ');
                  element['hearingDate'] = line.eq(0).find('span').text();
                  element['court'] = line.eq(1).find('div').children().eq(1).text();
                  element['judge'] = line.eq(1).find('div').children().eq(0).text();
                  element['istec-details'] = line.eq(2).find('span').eq(1).text().replace(/\s\s+/g, ' ');
                  line.eq(2).find('span').eq(1).remove();
                  element['istec'] = line.eq(2).find('span').text().replace(/\s\s+/g, ' ');
                  element['otvetchik-details'] = line.eq(3).find('span').eq(1).text().replace(/\s\s+/g, ' ');
                  line.eq(3).find('span').eq(1).remove();
                  element['otvetchik'] = line.eq(3).find('span').text().replace(/\s\s+/g, ' ');
                  data['items'].push(element)
                }
                back_to_python(data,getcookies());
            }, 10000 );
      } catch (err) {
        back_to_python( {'error': err},getcookies());
      };
})();
