-- SET SEARCH_PATH TO mundial ;

-- create or replace function view_gr(grp varchar) returns setof reprezentacja as
-- $$
--     select * from reprezentacja where grupa=grp order by nazwa;
-- $$
-- language sql;

-- create or replace function rep_name(id_r int) returns varchar(16) as
-- $$
--     declare
--         id_rep alias for $1;
--         name varchar;
--     begin
--         select into name nazwa from reprezentacja
--         where id_reprezentacja = id_rep;
--         return name;
--     end;
-- $$
-- language 'plpgsql';

create or replace view mecz_view (id_mecz, id_reprezentacja1, nazwa1, id_reprezentacja2, nazwa2) as 
    select mecz.id_mecz, mecz.id_reprezentacja1, r1.nazwa, mecz.id_reprezentacja2, r2.nazwa, mecz.data_rozpoczecia
    from mecz, reprezentacja r1, reprezentacja r2
    where mecz.id_reprezentacja1 = r1.id_reprezentacja and mecz.id_reprezentacja2 = r2.id_reprezentacja order by id_mecz;

create or replace view wynik_view (id_mecz, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2) as 
    select mecz_view.id_mecz, mecz_view.id_reprezentacja1, mecz_view.nazwa1, wynik_meczu.wynik_reprezentacja1, mecz_view.id_reprezentacja2, mecz_view.nazwa2, wynik_meczu.wynik_reprezentacja2, mecz_view.data_rozpoczecia 
    from mecz_view, wynik_meczu
    where mecz_view.id_mecz = wynik_meczu.id_mecz order by id_mecz;

create or replace view sedziowie_view (id_sedzia, imie, nazwisko, federacja) as
    select sedzia.id_sedzia, sedzia.imie, sedzia.nazwisko, federacja.nazwa
    from sedzia, federacja
    where sedzia.id_federacja = federacja.id_federacja order by nazwisko;

create or replace view sedziaid_mecz_view (id_mecz, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2, id_sedzia) as 
    select wynik_view.id_mecz, wynik_view.id_reprezentacja1, wynik_view.nazwa1, wynik_view.wynik1, wynik_view.id_reprezentacja2, wynik_view.nazwa2, wynik_view.wynik2, mecz.id_sedzia
    from mecz, wynik_view
    where mecz.id_mecz = wynik_view.id_mecz order by id_mecz;

create or replace view sedzia_mecz_view (id_mecz, id_sedzia, imie, nazwisko, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2) as 
    select sedziaid_mecz_view.id_mecz, sedziaid_mecz_view.id_sedzia, sedzia.imie, sedzia.nazwisko, sedziaid_mecz_view.id_reprezentacja1, sedziaid_mecz_view.nazwa1, sedziaid_mecz_view.wynik1, sedziaid_mecz_view.id_reprezentacja2, sedziaid_mecz_view.nazwa2, sedziaid_mecz_view.wynik2
    from sedziaid_mecz_view, sedzia
    where sedziaid_mecz_view.id_sedzia = sedzia.id_sedzia order by id_mecz;

create or replace view pilkarz_view (id_pilkarz, numer, imie, nazwisko, id_reprezentacja, reprezentacja) as
    select pilkarz.id_pilkarz, pilkarz.numer, pilkarz.imie, pilkarz.nazwisko, pilkarz.id_reprezentacja, reprezentacja.nazwa 
    from pilkarz left join reprezentacja 
    on pilkarz.id_reprezentacja = reprezentacja.id_reprezentacja order by pilkarz.id_pilkarz;

create or replace view reprezentacja_view (id_reprezentacja, nazwa, grupa, konfederacja) as
    select r.id_reprezentacja, r.nazwa, r.grupa, kf.nazwa
    from reprezentacja r
    left join federacja kf
    on r.id_federacja = kf.id_federacja
    order by r.id_reprezentacja;

create or replace view selekcjoner_view (id_reprezentacja, reprezentacja, imie, nazwisko) as
    select s.id_reprezentacja, r.nazwa, s.imie, s.nazwisko
    from selekcjoner s
    full outer join reprezentacja r
    on r.id_reprezentacja = s.id_reprezentacja
    order by s.id_reprezentacja;

create or replace view stadion_view (id_mecz, id_stadion, nazwa, miasto) as
    select m.id_mecz, m.id_stadion, st.nazwa, st.miasto
    from mecz m
    left join stadion st
    on m.id_stadion = st.id_stadion
    order by m.id_mecz;

create or replace view stadion_mecze_view (id_mecz, id_stadion, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2) as
    select st.id_mecz, st.id_stadion, w.id_reprezentacja1, w.nazwa1, w.wynik1, w.id_reprezentacja2, w.nazwa2, w.wynik2
    from stadion_view st
    left join wynik_view w
    on w.id_mecz = st.id_mecz
    order by st.id_mecz;

create or replace function remove_if_draw00 () returns trigger language z as
$$
    begin
        if NEW.wynik_reprezentacja1 = 0 and NEW.wynik_reprezentacja2 = 0 then
            delete from zdarzenie_boiskowe where id_mecz = NEW.id_mecz;
        end if;
        return new;
    end;
$$;

create trigger wynik_check
    before update on wynik_meczu
    for each row execute procedure remove_if_draw00();

create or replace function too_much_check () returns trigger language plpgsql as
$$
    declare 
        wynik int;
    begin
        if NEW.id_reprezentacja = (select id_reprezentacja1 from wynik_view where id_mecz = NEW.id_mecz) then
            wynik = (select wynik1 from wynik_view where id_mecz = NEW.id_mecz);
        else
            wynik = (select wynik2 from wynik_view where id_mecz = NEW.id_mecz);
        end if;
        if (NEW.liczba_goli  + (select sum(liczba_goli) from zdarzenie_boiskowe where id_mecz = NEW.id_mecz and id_reprezentacja = NEW.id_reprezentacja)) >= wynik then
            return null;
        else
            return new;
        end if;
    end;
$$;

create trigger gole_check
    before insert on zdarzenie_boiskowe
    for each row execute procedure too_much_check();

create or replace view strzelcy_view (id_mecz, id_reprezentacja, reprezentacja, id_pilkarz, imie, nazwisko, numer, liczba_goli) as
    select z.id_mecz, z.id_reprezentacja, p.reprezentacja, z.id_pilkarz, p.imie, p.nazwisko, p.numer, z.liczba_goli
    from zdarzenie_boiskowe z
    left join pilkarz_view p
    on z.id_pilkarz = p.id_pilkarz
    order by z.id_mecz;

create or replace view ranking_strzelcow (id_reprezentacja, reprezentacja, id_pilkarz, imie, nazwisko, suma_goli) as
    select s.id_reprezentacja, s.reprezentacja, s.id_pilkarz, s.imie, s.nazwisko, sum(s.liczba_goli) suma_goli
    from strzelcy_view s
    group by s.id_reprezentacja, s.reprezentacja, s.id_pilkarz, s.imie, s.nazwisko
    order by suma_goli desc;

create or replace view grupa_mecze_view (id_mecz, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2, grupa) as
    select m.id_mecz, m.id_reprezentacja1, m.nazwa1, m.wynik1, m.id_reprezentacja2, m.nazwa2, m.wynik2, r.grupa
    from wynik_view m
    left join reprezentacja r
    on m.id_reprezentacja1 = r.id_reprezentacja
    where m.id_mecz < 49
    order by m.id_mecz;

-- create or replace view mecze_grupa_view (id_mecz, grupa, id_reprezentacja1, nazwa1, wynik1, id_reprezentacja2, nazwa2, wynik2)