%% Clear
clear all; clc
addpath("k-Wave/")
%% Simulation grid parameter
Nx = 124;               % number of grid points in the x (row) direction
Ny = 60;               % number of grid points in the y (column) direction
dx = 5e-3;            % grid points spacing in the x direction [m]
dy = 5e-3;            % grid points spacing in the y direction [m]

kgrid = kWaveGrid(Nx, dx, Ny, dy);

for mat = ['bois','verre','acier']
switch mat
    case 'bois'
        % SoundSpeed = ;   
        % Density = ; 
    case 'verre'
        % SoundSpeed = 5640; % [m/s]
        % Density = 2240; % [kg/m^3]
    case 'acier'
        % SoundSpeed = 5640; % [m/s]
        % Density = 2240; % [kg/m^3]
end

for forme = ['rectangle','coin','coin_trou']
medium.sound_speed = SoundSpeed*ones(Nx, Ny);
medium.density = Density*ones(Nx, Ny);
medium.alpha_coeff = 0.75;              % [dB/(MHz^y cm)]
medium.alpha_power = 1.5;
airSpeed = 330;     % [m/s]
airDensity = 10;    % [kg/m^3]

for i = 1:Nx
    for j = 1:Ny
        if i < 4 || i > (Nx-4) || j < 4 || j > (Ny-4)
            medium.sound_speed(i,j) = airSpeed;
            medium.density(i,j) = airDensity;
        end
    end
end

for i = 1:Nx
    for j = 1:Ny
        if strcmp(forme,'coin_trou')
        if i > 70 && i < 80 && j >= (Ny/4-8) && j <= (Ny/4+8)
            medium.sound_speed(i,j) = airSpeed;
            medium.density(i,j) = airDensity;
        end
        end
        if strcmp(forme,'coin_trou') | strcmp(forme,'coin')
        if  j >= 25 && j <= 18 && i >= 45 && i <= 50 ||  j <= (24-i/2)
            medium.sound_speed(i,j) = airSpeed;
            medium.density(i,j) = airDensity;
        end
        end
    end
end

%% Define sensor
clear sensor

% Emplacement des senseurs
x = round(linspace(5,119,100));
y = round(linspace(5,55,50));
[X,Y] = meshgrid(x,y);
sensorXGrid = reshape(X,[],1);
sensorYGrid = reshape(Y,[],1);

sensor.mask = [kgrid.x_vec(sensorXGrid)'; kgrid.y_vec(sensorYGrid)'];

%% Sensor definition (utilisé comme émetteur pour former le dictionnaire)
sensor_pos_mat = [[115,15];[60,30];[10,50]];
for sensor_idx = [1,2,3]
sourceGrid = sensor_pos_mat(sensor_idx,:); % Sera utilisé comme capteur apres la formation du dictionnaire
source_radius = floor(0.01/dx);         % [grid points] (Taille d'un doigt)
source_magnitude = 10;                  % [Pa]
source_1 = source_magnitude*makeDisc(Nx, Ny, sourceGrid(1), sourceGrid(2), source_radius);
source.p0 = source_1;

%% Simulation pour former le dictionnaire
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor,...
    'PMLSize', 2, 'PMLInside', false, 'DataCast', 'single');

%% Formation du dictionnaire
dic = flip(sensor_data,1); % retournement temporel

%% Simu avec la source du dictionnaire comme senseur et avec une source random
% Define sensor
clear sensor
sensorX = sourceGrid(1);     % [gridPoint]
sensorY = sourceGrid(2);     % [gridPoint]

% On transforme les points de la grille de simulation en position
% cartésienne.
sensor.mask = [kgrid.x_vec(sensorX)'; kgrid.y_vec(sensorY)'];

%% Source definition
source_pos_mat = [[90 20];[]]; %Mettre 5 positions
for source_pos_idx = [1 2 3 4 5]
randSourceGrid = source_pos_mat(source_pos_idx,:); 
source_radius = floor(0.01/dx);         % [grid points] (Taille d'un doigt)
source_magnitude = 10;                  % [Pa]
source_1 = source_magnitude*makeDisc(Nx, Ny, randSourceGrid(1), randSourceGrid(2), source_radius);
source.p0 = source_1;

% Pour l'affichage, on transforme les points de la grille de simulation en
% position cartésienne. 
source_x_pos = kgrid.x_vec(randSourceGrid(1));         % [grid points]
source_y_pos = kgrid.y_vec(randSourceGrid(2));         % [grid points]

%% Visualisation de la grille de simulation
figure;
imagesc(kgrid.y_vec*1e3, kgrid.x_vec*1e3, medium.sound_speed); axis image
ylabel('x - position [mm]')
xlabel('y - position [mm]')
c = colorbar;
c.Label.String = 'Speed of sound';
hold on;
plot(sensor.mask(2,:)*1e3, sensor.mask(1,:)*1e3, 'r.')
plot(source_y_pos*1e3, source_x_pos*1e3, 'b+')
legend('Sensor', 'Source')

%% Simulation
sensor_data = kspaceFirstOrder2D(kgrid, medium, source, sensor,...
    'PMLSize', 2, 'PMLInside', false, 'DataCast', 'single');

%% Correlation map
corr = zeros(1,length(sensorXGrid));
for i = 1:length(sensorXGrid)
    corr(i) = max(xcorr(sensor_data/norm(sensor_data),dic(i,:)/norm(dic(i,:))));
    %corr(i) = max(xcorr(sensor_data,dic(i,:),'coeff'));
end
corr_mat = reshape(corr,size(X,1),size(X,2));
corr_mat = flip(flip(corr_mat',2),1);

sensor_x_pos = kgrid.x_vec(x);         % [grid points]
sensor_y_pos = kgrid.y_vec(y);         % [grid points]

figure;
imagesc(sensor_y_pos*1e3,sensor_x_pos*1e3,corr_mat); axis image; colormap('gray');
xlabel('x pos (mm)')
ylabel('y pos (mm)')
c = colorbar;
c.Label.String = 'Correlation';
%% Sauvegarde des données
% Sauvegarder les données pour les réutiliser plus tard, où pour les
% exporter vers python. Pour load dans python, utiliser scipy.io.loadmat()
%source_idx: 1 = en-bas a gauche, 2 = centre, 3 = en-haut a droite
save([mat,'_',forme,'_',sensor_idx, '.mat'], 'corr_mat')

end
end
end
end