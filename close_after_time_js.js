(function(){
    setTimeout(
        function() {
            // if($('html:contains("Ошибка 429")').length > 0)  {close_after_time({'error': 'error 429'})};
            close_after_time(document.documentElement.outerHTML);
        }, 30000 );
        
})();