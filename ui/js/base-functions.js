/*
Author: Ovchinnikov Anatoly Vladimirovich
Email: east@thyloved.ru
Version: 1.0-2017
 */
Date.prototype.ddmmyyyy = function() {
	var yyyy = this.getFullYear().toString();
	var mm = (this.getMonth()+1).toString();
	var dd  = this.getDate().toString();
	return (dd[1]?dd:'0'+dd[0])+'.'+(mm[1]?mm:'0'+mm[0])+'.'+yyyy;
};
window.showOutState = function(pins){
    if ( Object.keys(pins).length > 0 ){
	for(var i in pins){
	  var cls_on = "btn-success";
	  var cls_off = "btn-default";
	  var add = cls_on;
	  var remove = cls_off;
	  if ( pins[i]["value"] == 0 ){
	      add = cls_off;
	      remove = cls_on;
	  }
	  document.querySelector('a[data-io="'+pins[i]["pin"]+'"]').classList.add(add);
	  document.querySelector('a[data-io="'+pins[i]["pin"]+'"]').classList.remove(remove);
	  if ( pins[i]["function"] != "OUT" ){
	      document.querySelector('a[data-io="'+pins[i]["pin"]+'"]').classList.add("disabled");
	  }
	  document.querySelector('a[data-io="'+pins[i]["pin"]+'"] .pin-func').innerHTML='('+pins[i]["function"]+')';
	}
    }
}
window.leftPad = function(number, targetLength){
    var output = number + '';
    while (output.length < targetLength){
        output = '0' + output;
    }
	return output;
}
window.setDate = function(){
	var days={0:'Вск',1:'Пн',2:'Вт',3:'Ср',4:'Чт',5:'Пт',6:'Сб'};
	var today = new Date();
	var d = today.getDay();
	var h = today.getHours();
	var m = today.getMinutes();
	document.getElementById('time').innerHTML= days[d] + ', ' + today.ddmmyyyy() + ' ' + leftPad(h,2) + ':' + leftPad(m,2);
}
window.setCalendar = function(){
  $('#datetimepicker12').datetimepicker({
    format: "DD.MM.YYYY H:m",
    inline: true,
    sideBySide: true,
    locale:'ru'
  });
}
window.tabSwitcher = function(){
	$("div.list-group>a").mousedown(function(e) {
	    e.preventDefault();
	    $(this).siblings('a.active').removeClass("active");
	    $(this).addClass("active");
	});
}
window.setTimepicker = function(){
  $('#ts,#te').datetimepicker({
    format: "HH:mm",
    inline: true,
    sideBySide: true,
    locale:'ru'
  });
}
window.setSchedulesLoader = function(){
  $(document).on('mousedown','.loadSchedule',function(){
     var d = $('.list-group a.active').data('day-n');
     var o = $('#out-number').data('out-n');
     WebView.loadSchedule(o,d);
  });
}
window.initSchedulerPage = function(p){
    tabSwitcher();
    setTimepicker();
    setSchedulesLoader();
    setRemover();
    setAdder();
    var pins = extractOutputsFromState(p);
    setPinSelector(pins);
    setDaySelector();
    setCopyDay();
    setCopyWeek();
    $('.list-group a:first').trigger('mousedown');
}
window.setCopyDay = function(){
    $(document).on('mousedown','.copyDay',function(){
        var dd      = $('#week-day').data('d');
        var cd      = $('.list-group a.active').data('day-n');
        var o       = $('#out-number').data('out-n');
        WebView.cloneSchedule(cd,dd,o);
    });
}
window.setCopyWeek = function(){
    $(document).on('mousedown','.copyWeek',function(){
        var cd      = $('.list-group a.active').data('day-n');
        var o       = $('#out-number').data('out-n');
        WebView.cloneSchedule(cd,'w',o);
    });
}
window.setDaySelector = function(){
    var days = ["Пн","Вт","Ср","Чт","Пт","Сб","Вс"];
    $(document).on('mousedown','.selectDay',function(){
        var d       = $('#week-day').text();
        var index   = days.indexOf(d);
        var dir     = parseInt( $(this).data('direction') );
        var ni      = index+dir;
        var nd      = days[ni];
        if ( typeof nd == 'undefined' ){
            if( dir > 0 ){
                ni = 0;
                nd = days[ni];
            }else{
                ni = days.length-1;
                nd = days[ni];
            }
        }
        $('#week-day').data("d",ni).text(nd);
    });
}
window.setPinSelector = function(pins){
    if( pins.length > 0 ){
        $('#out-number').data("out-n",pins[0]).text(pins[0]);
    }
    $(document).on('mousedown','.selectPin',function(){
        var pin     = parseInt( $('#out-number').data("out-n") );
        var index   = pins.indexOf(pin);
        var dir     = parseInt( $(this).data('direction') );
        var o       = pins[index+dir];
        if ( typeof o == 'undefined' ){
            if( dir > 0 ){
                o = pins[0];
            }else{
                o = pins[ pins.length-1 ];
            }
        }
        $('#out-number').data("out-n",o).text(o);
        var d = $('.list-group a.active').data('day-n');
        WebView.loadSchedule(o,d);
    });
}
window.extractOutputsFromState = function(obj){
    var r = [];
    if ( Object.keys(obj).length > 0 ){
        $.each(obj,function(k,v){
           if( v.function == 'OUT' ){
               r.push(v.pin)
           }
        });
        r.sort();
    }
    return r;
}
window.listIntervals = function(intervals,d){
    $('#schedules').html('<span class="no-schedule centerer">Расписания не задано</span>');
    if(intervals&&intervals.length>0){
        $('#schedules').empty();
        var a = '<a href="javascript:void(0)" class="btn btn-default">{time}<i class="glyphicon glyphicon-remove remove-schedule" data-ts="{time-s}" data-te="{time-e}"></i></a>';
        $.each(intervals,function(i,v){
            t = v.split('-');
            var a_ = a.replace('{time}',v).replace('{time-s}',t[0]).replace('{time-e}',t[1]);
            $('#schedules').append(a_);
        });
    }
}
window.setRemover = function(){
  $(document).on('mousedown','.remove-schedule',function(){
     var d = $('.list-group a.active').data('day-n');
     var o = $('#out-number').data('out-n');
     var ts = $(this).data('ts');
     var te = $(this).data('te');
     WebView.removeSchedule(d,o,ts,te);
  });
}
window.mw = function(msg){
    $('#modal-window .modal-body p').html(msg);
    $('#modal-window').modal('show');
}
window.setAdder = function(){
  $(document).on('mousedown','.addSchedule',function(){
     var d = $('.list-group a.active').data('day-n');
     var o = $('#out-number').data('out-n');
     var ts = $('#ts').data('date');
     var te = $('#te').data('date');
     var ts1 = parseInt(ts.replace(':',''));
     var te1 = parseInt(te.replace(':',''));
     if (te1<=ts1){
        window.mw('Время выключения не может быть меньше или равно времени включения');
        return;
     }
     var intersects = false;
     $('#schedules a i').each(function(i,o){
        var ts2 = parseInt($(o).data('ts').replace(':',''));
        var te2 = parseInt($(o).data('te').replace(':',''));
        if( ts1 <= te2 && ts2 <= te1 ){
            intersects = true;
            return false;
        }
     });
     if (intersects){
        window.mw('Интервалы включения одного выхода не могут пересекаться');
        return;
     }
     WebView.addSchedule(d,o,ts,te);
  });
}
window.showLog = function(log){
    var trs = '<tr><td class="no-schedule" colspan="10" style="text-align;">События отсутствуют</td></tr>';
    if ( Object.keys(log).length > 0 ){
        trs = '';
        $.each(log, function(i,v){
            var t_ = '';
            var d_ = '';
            if (v[4]){
                var d = v[4].split(' ');
                if (d[1]){
                    t_=d[1];
                }
                if (d[0]){
                    d[0] = d[0].split('-');  
                    d_ = d[0][2]+'.'+d[0][1]+'.'+d[0][0];
                }
            }
            var o = '';
            try{
                v[1] = JSON.parse(v[1]);
                if(v[1]['channel']){o+='. Номера выходов: '+JSON.stringify(v[1]['channel'])+'. Установлено значение: '+(v[1]['value']?1:0)};
            }catch(e){}
            trs += '<tr><td>'+(i+1)+'</td><td>'+(t_+' '+d_)+'</td><td>'+(v[2]?v[2]:'-')+o+'</td><td>'+(v[3]?v[3]:'-')+'</td></tr>';
        });
    }
    $('#log-table tbody').html(trs);
}
window.setMainButtonsEvents = function(run){
    var rm = 'red';
    var add = 'green';
    if (run==false){
        var rm = 'green';
        var add = 'red';
    }
    $('.run-indicator').removeClass(rm).addClass(add);

    $(document).on('mousedown','#start',function(){
        $('.run-indicator').removeClass('red').addClass('green');
        WebView.start();
    });
    $(document).on('mousedown','#stop',function(){
        $('.run-indicator').removeClass('green').addClass('red');
        WebView.stop();
    });
}