(function(){
    
    
    $('#sug-participants input').val('[case_number]');
    $('#sug-participants input').attr('class','');
    $('#b-form-submit button').click();
    $('#b-form-submit button').click();
    if($('html:contains("Ошибка 429")').length > 0)  {back_to_python({'error': 'error 429'})};


    try { setTimeout(
            function() {
                if($('html:contains("Ошибка 429")').length > 0)  { back_to_python({'error': 'error 429'}); };
                data = {};
                data['uid'] = $('#b-cases a').attr('href').split('/').pop();
                data['case'] = $('#b-cases a').attr('text').replace(/\s\s+/g, ' ');
                data['court'] = $('#b-cases .court div').children().eq(1).text();
                data['judge'] = $('#b-cases .court div').children().eq(0).text();
                data['istec-details'] = $('#b-cases .plaintiff span').eq(1).text().replace(/\s\s+/g, ' ');
                $('#b-cases .plaintiff span').eq(1).remove()
                data['istec'] = $('#b-cases .plaintiff span').text().replace(/\s\s+/g, ' ');
                data['otvetchik-details'] = $('#b-cases .respondent span').eq(1).text().replace(/\s\s+/g, ' ');
                $('#b-cases .respondent span').eq(1).remove()
                data['otvetchik'] = $('#b-cases .respondent span').text().replace(/\s\s+/g, ' ');
                back_to_python(data);
            }, 15000 );
      } catch (err) {
        back_to_python( {'error': err});
      };
})();
